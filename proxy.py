"""Local proxy server that intercepts DeepSeek API calls and tracks token usage."""
import json
import logging
from urllib.parse import urljoin

import flask
import requests

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, PROXY_HOST, PROXY_PORT
from tracker import get_tracker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PROXY] %(message)s")
log = logging.getLogger("proxy")

app = flask.Flask(__name__)

# Headers to strip from client request before forwarding
STRIP_HEADERS = {"Host", "Content-Length", "Transfer-Encoding"}


def _forward_headers() -> dict:
    headers = {}
    for key, value in flask.request.headers:
        if key not in STRIP_HEADERS:
            headers[key] = value
    headers["Authorization"] = f"Bearer {DEEPSEEK_API_KEY}"
    return headers


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """Proxy chat completions, tracking token usage."""
    body = flask.request.get_data()
    req_json = flask.request.get_json(silent=True) or {}
    stream = req_json.get("stream", False)

    target_url = urljoin(DEEPSEEK_BASE_URL, "/v1/chat/completions")

    if stream:
        return _proxy_stream(target_url, body)
    else:
        return _proxy_normal(target_url, body)


@app.route("/v1/models", methods=["GET"])
def list_models():
    """Proxy models list."""
    target_url = urljoin(DEEPSEEK_BASE_URL, "/v1/models")
    resp = requests.get(target_url, headers=_forward_headers(), timeout=10)
    return (resp.content, resp.status_code, resp.headers.items())


@app.route("/user/balance", methods=["GET"])
def balance():
    """Proxy balance check to api.deepseek.com/user/balance."""
    target_url = urljoin(DEEPSEEK_BASE_URL, "/user/balance")
    resp = requests.get(target_url, headers=_forward_headers(), timeout=10)
    return (resp.content, resp.status_code, resp.headers.items())


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def catch_all(path):
    """Forward any other request."""
    target_url = urljoin(DEEPSEEK_BASE_URL, path)
    method = flask.request.method
    headers = _forward_headers()
    data = flask.request.get_data() if method in ("POST", "PUT", "PATCH") else None

    resp = requests.request(method, target_url, headers=headers, data=data, timeout=30)
    return (resp.content, resp.status_code, resp.headers.items())


def _proxy_normal(target_url: str, body: bytes):
    """Handle non-streaming request."""
    try:
        resp = requests.post(
            target_url,
            headers=_forward_headers(),
            data=body,
            timeout=120,
        )
    except requests.RequestException as e:
        log.error("Proxy request failed: %s", e)
        return {"error": str(e)}, 502

    # Extract usage info from response
    try:
        data = resp.json()
        usage = data.get("usage") or {}
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        model = data.get("model", "default")

        if prompt_tokens or completion_tokens:
            tracker = get_tracker()
            tracker.record_usage(prompt_tokens, completion_tokens, model)
            log.info("Recorded: +%d in +%d out (%s)", prompt_tokens, completion_tokens, model)
    except (ValueError, KeyError) as e:
        log.warning("Could not parse usage from response: %s", e)

    return (resp.content, resp.status_code, dict(resp.headers))


def _proxy_stream(target_url: str, body: bytes):
    """Handle streaming (SSE) request."""
    try:
        upstream = requests.post(
            target_url,
            headers=_forward_headers(),
            data=body,
            stream=True,
            timeout=120,
        )
    except requests.RequestException as e:
        log.error("Stream proxy request failed: %s", e)
        return {"error": str(e)}, 502

    def generate():
        prompt_tokens = 0
        completion_tokens = 0
        model = "default"

        for line in upstream.iter_lines(decode_unicode=True):
            if not line:
                yield "\n"
                continue

            yield line + "\n"

            # Parse SSE data lines
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    continue
                try:
                    chunk = json.loads(data_str)
                    if "model" in chunk:
                        model = chunk["model"]
                    usage = chunk.get("usage") or {}
                    if usage.get("prompt_tokens"):
                        prompt_tokens = usage["prompt_tokens"]
                    if usage.get("completion_tokens"):
                        completion_tokens = usage["completion_tokens"]
                except json.JSONDecodeError:
                    pass

        # Record usage after stream ends
        if prompt_tokens or completion_tokens:
            tracker = get_tracker()
            tracker.record_usage(prompt_tokens, completion_tokens, model)
            log.info("Recorded (stream): +%d in +%d out (%s)", prompt_tokens, completion_tokens, model)

    resp_headers = {k: v for k, v in upstream.headers.items()
                    if k.lower() not in ("content-length", "transfer-encoding")}

    return flask.Response(generate(), status=upstream.status_code, headers=resp_headers,
                          content_type=upstream.headers.get("content-type", "text/event-stream"))


def start_proxy():
    """Start the proxy server (blocking)."""
    log.info("Proxy starting on %s:%s", PROXY_HOST, PROXY_PORT)
    app.run(host=PROXY_HOST, port=PROXY_PORT, debug=False, use_reloader=False)
