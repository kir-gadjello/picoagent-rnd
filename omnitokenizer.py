import os
import re
import json
import urllib.request
import tiktoken
import urllib.error


def check_azure_or_openai(string):
    pattern = re.compile(r"(?i)azure|openai", re.IGNORECASE)
    return pattern.search(string) is not None


def url_has_host(url):
    parsed = urllib.parse.urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def debug(*args):
    if os.environ.get("OMNITOKENIZER_DEBUG"):
        print(*args)


def send_test_request(url, post_data, headers={}):
    try:
        debug("test api:", url, post_data, headers)
        request = urllib.request.Request(
            url,
            data=json.dumps(post_data).encode("utf-8"),
            method="POST",
            headers=headers,
        )
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        debug(e)
    except Exception as e:
        debug(e)

    return None


saved_tokenizers = {}
api_found = None

supported_tokenizer_apis = dict(
    tabbyapi=["/v1/token/encode", lambda s: dict(text=s), lambda j: j["tokens"]],
    llamacpp=["/tokenize", lambda s: dict(content=s), lambda j: j],
)


def get_full_api_path(api_base, path):
    _api_base = api_base.rstrip("/").rstrip("/v1")
    return f"{_api_base}{path}"


def automatic_api_guess(api_base, headers={}):
    if not api_base:
        raise Exception("OPENAI_API_BASE not given to guessing engine")

    for api, api_config in supported_tokenizer_apis.items():
        path, compose_fn, extract_fn = api_config
        try:
            check_url = get_full_api_path(api_base, path)
            resp = send_test_request(check_url, compose_fn("test message"), headers)
            tokens = extract_fn(resp)
            if tokens and len(tokens):
                print(f'[omnitokenizer]: found api "{api}" tokenizer at {check_url}')
                return api
        except Exception:
            continue

    return False


def tokenize(text, model=None, api_key=None):
    global api_found

    oai_api_base = os.environ.get("OPENAI_API_BASE")

    if check_azure_or_openai(oai_api_base) or not oai_api_base:
        if model.startswith("gpt-"):
            if model not in saved_tokenizers:
                print(f"[omnitokenizer]: loading tiktoken encoder for {model}")
                saved_tokenizers[model] = tiktoken.encoding_for_model(model)
            return saved_tokenizers.get(model)(text)
        else:
            raise Exception(f"Unknown model for openai or azure api: {model}")

    headers = {}

    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    elif "OPENAI_API_KEY" in os.environ:
        api_key = os.environ["OPENAI_API_KEY"]
        headers["Authorization"] = "Bearer " + api_key

    headers["Content-Type"] = "application/json"

    if api_found is None:
        api_found = automatic_api_guess(oai_api_base, headers)

    if api_found is False or api_found not in supported_tokenizer_apis:
        raise Exception(
            f"[omnitokenizer]: Automatic tokenizer api guess failed, supported apis: {list(supported_tokenizer_apis.keys())}"
        )

    tokens_api = supported_tokenizer_apis[api_found]
    path, compose_fn, extract_fn = tokens_api
    api_url = get_full_api_path(oai_api_base, path)

    data = json.dumps(compose_fn(text)).encode("utf-8")

    req = urllib.request.Request(api_url, data, headers)
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())

    return extract_fn(result)


if __name__ == "__main__":
    print("[omnitokenizer]: TEST MODE")
    print(f"Environment: OPENAI_API_BASE={os.environ.get('OPENAI_API_BASE')}")
    ret = tokenize("test message")
    print(f'tokenize("test message") = {ret}')
