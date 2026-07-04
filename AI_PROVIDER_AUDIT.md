# RC22 AI Provider Audit

## Scope

Audited only the AI provider path:

Desktop GUI -> Production -> LucidAI -> Gemini Client -> HTTP Client -> TLS -> HTTPS

No generator, retrieval, knowledge, GUI, packaging, exporter, prompt, fallback, or production behavior changes were made.

## Provider Stack

1. Desktop GUI calls the production flow.
2. Production content generation uses `hgpt_ai_os.content.generator.ContentGenerator`.
3. `ContentGenerator` constructs `hgpt_ai_os.ai.client.LucidAI`.
4. `LucidAI` delegates to `GeminiProvider`.
5. `GeminiProvider` uses `GeminiClient` in live mode when both conditions are true:
   - `USE_REAL_GEMINI` is enabled.
   - `GOOGLE_API_KEY` is present.
6. `GeminiClient` sends HTTPS requests to:
   - `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`

## 1. HTTP Library In Use

The active Gemini transport uses Python standard library `urllib.request`.

Evidence:

- `src/hgpt_ai_os/ai/gemini_client.py` imports `urllib.request`.
- `GeminiClient.generate()` builds a `urllib.request.Request`.
- The request is executed with `urllib.request.urlopen()`.

Installed but not used by the active provider transport:

- `requests`
- `httpx`
- `google-genai`
- `urllib3`

## 2. SSL Verification Configuration

Before the RC22 patch, SSL verification was not configured in application code.

`urllib.request.urlopen()` was called without an explicit `context`, so Python used the interpreter/OpenSSL default verification paths.

Observed default verification path from the repo virtual environment:

```text
openssl_cafile=/Library/Frameworks/Python.framework/Versions/3.12/etc/openssl/cert.pem
openssl_capath=/Library/Frameworks/Python.framework/Versions/3.12/etc/openssl/certs
```

The default CA file did not exist:

```text
/Library/Frameworks/Python.framework/Versions/3.12/etc/openssl/cert.pem: No such file or directory
```

After the RC22 patch, `GeminiClient` creates an explicit TLS context:

```python
ssl.create_default_context(cafile=certifi.where())
```

and passes it to `urllib.request.urlopen()`.

## 3. CA Source In Use

Before the RC22 patch:

- `certifi` was installed but unused by the active Gemini transport.
- The macOS system keychain was not explicitly used by the provider code.
- No custom CA bundle was found in the repository.
- Python/OpenSSL default paths were used.

After the RC22 patch:

- `certifi` is used explicitly for Gemini HTTPS verification.
- `certifi` is already pinned in `requirements.txt`.

Observed certifi bundle:

```text
/Users/macos/Desktop/HGPT_AI_OS_CLEAN/.venv/lib/python3.12/site-packages/certifi/cacert.pem
```

## 4. Failure Classification

Exact failure reproduced against the Gemini host with the repo virtual environment:

```text
URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)'))
```

Classification:

- Missing CA bundle: yes, for Python/OpenSSL default path.
- macOS certificate chain: not the direct cause found in provider code; the active Python build does not automatically use the macOS keychain here.
- Python environment: yes, the interpreter default CA path points to a missing file.
- certifi mismatch: no. `certifi` exists and succeeds when used explicitly.
- proxy: no evidence. `HTTP_PROXY`, `HTTPS_PROXY`, `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`, and `SSL_CERT_FILE` were unset in the audited shell.
- provider endpoint: no. The endpoint completed TLS successfully when `urllib` used `certifi`; the unauthenticated host probe then returned HTTP 404, proving HTTPS verification passed.

Root cause:

The active Gemini HTTP client relies on Python/OpenSSL default TLS trust paths, but the configured default CA file is missing. The installed `certifi` CA bundle is valid but was not wired into the `urllib` request path.

## 5. Minimum-Risk Production Fix

Use `certifi` explicitly in the Gemini provider transport and pass that SSL context to `urllib.request.urlopen()`.

Why this is minimum risk:

- It is confined to the AI provider layer.
- It preserves the current HTTP library.
- It preserves live/mock gating.
- It does not alter prompts, retrieval, generation, GUI, packaging, export, endpoint, payload, retry, or fallback behavior.
- It uses an existing pinned dependency.
- It fixes only TLS trust material selection for HTTPS verification.

## Patch Summary

Changed file:

- `src/hgpt_ai_os/ai/gemini_client.py`

Behavioral change:

- Gemini HTTPS requests now verify TLS using `certifi` instead of relying on a missing interpreter default CA file.

## Validation Steps

Run from `/Users/macos/Desktop/HGPT_AI_OS_CLEAN`.

1. Confirm the Python default CA file is missing:

```bash
.venv/bin/python - <<'PY'
import ssl
print(ssl.get_default_verify_paths())
PY
```

2. Reproduce the pre-fix failure without an explicit certifi context:

```bash
.venv/bin/python - <<'PY'
import ssl, urllib.request
print(ssl.get_default_verify_paths())
with urllib.request.urlopen("https://generativelanguage.googleapis.com/", timeout=10) as response:
    print(response.status)
PY
```

Expected pre-fix result:

```text
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
```

3. Confirm `certifi` verifies the Gemini host:

```bash
.venv/bin/python - <<'PY'
import ssl, urllib.error, urllib.request, certifi
context = ssl.create_default_context(cafile=certifi.where())
try:
    with urllib.request.urlopen("https://generativelanguage.googleapis.com/", timeout=10, context=context) as response:
        print(response.status)
except urllib.error.HTTPError as exc:
    print(exc.code)
PY
```

Expected result:

```text
404
```

HTTP 404 is acceptable for the host root and proves TLS verification completed.

4. Compile the provider layer:

```bash
PYTHONPYCACHEPREFIX=/tmp/lucid_pycache .venv/bin/python -m py_compile src/hgpt_ai_os/ai/gemini_client.py src/hgpt_ai_os/ai/client.py src/hgpt_ai_os/ai/__init__.py
```

5. Validate the patched Gemini client reaches HTTP handling instead of TLS failure:

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
from hgpt_ai_os.ai.gemini_client import GeminiClient
response = GeminiClient(api_key="invalid-test-key", retries=0, timeout=10).generate("", "TLS probe")
print(type(response).__name__)
print(response.error_type)
print(response.metadata.get("status_code"))
print("ssl" in str(response.metadata).lower())
PY
```

Expected result:

```text
AIProviderError
http_error
400
False
```
