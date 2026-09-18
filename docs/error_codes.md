# MVP error codes

| Code | Category | Default severity | Detection / recommended action |
|---|---|---:|---|
| `HTTP_404` | http | ERROR | HTTP 404; inspect crawl target or source removal. |
| `HTTP_429` | http | ERROR | HTTP 429; reduce concurrency/rate and respect retry-after. |
| `HTTP_5XX` | http | ERROR | HTTP 500+; inspect upstream availability and retry policy. |
| `AUTH_REDIRECT_TO_LOGIN` | auth | ERROR | Final URL is a login route; refresh session/auth adapter. |
| `AUTH_LOGIN_PAGE_RETURNED` | auth | ERROR | HTTP 200 content is a login form; refresh session or endpoint. |
| `EMPTY_PAGE` | content | ERROR | HTTP 200 with no usable text; inspect extraction/rendering. |
| `VERY_LOW_CONTENT` | content | WARNING | Fewer than 20 words; review page type and extraction. |
| `SOFT_404` | content | ERROR | HTTP 200 with not-found markers and short/404-like content. |
| `CAPTCHA_PAGE` | access | CRITICAL | CAPTCHA/human verification markers; use authorized browser flow. |
| `ANTI_BOT_PAGE` | access | CRITICAL | Cloudflare/access-denied/bot markers; inspect crawl access. |
| `ENCODING_MOJIBAKE` | encoding | WARNING | UTF-8/legacy decode artifacts; correct charset handling. |
| `UNICODE_REPLACEMENT_CHAR` | encoding | WARNING | Replacement character present; recover original bytes/charset. |
| `CLEAN_RESULT_EMPTY` | cleaning | ERROR | Extracted content is substantial but clean result is empty. |
| `CLEANING_OVER_AGGRESSIVE` | cleaning | WARNING | Clean retention below 10%; inspect cleaning rules/source profile. |
| `EXACT_DUPLICATE_CONTENT` | duplicate | WARNING | SHA-256 normalized content appears on multiple pages; dedupe/canonicalize. |
