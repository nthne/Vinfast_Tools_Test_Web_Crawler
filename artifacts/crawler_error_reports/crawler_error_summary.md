# Crawler Error Summary

> Cumulative, concise summary of error signatures observed by the report tool.

| Metric | Value |
|---|---:|
| Unique crawl jobs | 7 |
| Error signatures | 32 |
| Total failed-page observations | 897 |
| Additional QA findings | 2 |
| Last updated (UTC) | `2026-09-18T05:01:40.972729+00:00` |

## Error types

| Rank | Error code | Short message | Total pages | Jobs | Detail report |
|---:|---|---|---:|---:|---|
| 1 | `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed | 315 | 5 | [errors/crw_permanent_3b1a353a482c.md](errors/crw_permanent_3b1a353a482c.md) |
| 2 | `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP discovery failed: error sending request | 253 | 5 | [errors/crw_permanent_2ba5aa22751c.md](errors/crw_permanent_2ba5aa22751c.md) |
| 3 | `CRW_PERMANENT` | js_escalation_failed: Renderer error: No JS renderer available | 188 | 1 | [errors/crw_permanent_b1e9c9438157.md](errors/crw_permanent_b1e9c9438157.md) |
| 4 | `NO_PROXY_AVAILABLE` | HTTP_403 | 38 | 1 | [errors/no_proxy_available_2e5558325302.md](errors/no_proxy_available_2e5558325302.md) |
| 5 | `CRWTEMPORARYERROR` | crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP discovery failed: error sending request | 11 | 2 | [errors/crwtemporaryerror_0e0158cf0817.md](errors/crwtemporaryerror_0e0158cf0817.md) |
| 6 | `UNSAFEDOWNLOADURL` | Connected peer differs from the validated DNS result | 10 | 3 | [errors/unsafedownloadurl_a370df1de898.md](errors/unsafedownloadurl_a370df1de898.md) |
| 7 | `CRW_PERMANENT` | Target returned 400 Bad Request | 9 | 2 | [errors/crw_permanent_ddabd5c2027f.md](errors/crw_permanent_ddabd5c2027f.md) |
| 8 | `UNSAFE_TARGET_URL` | Download host could not be resolved (add the host to ssrf_allowed_hosts if this is intended) | 9 | 3 | [errors/unsafe_target_url_b1ec305ad5b4.md](errors/unsafe_target_url_b1ec305ad5b4.md) |
| 9 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (2897 bytes, 46 chars visible)) | 7 | 2 | [errors/crw_permanent_eadc3334c5d1.md](errors/crw_permanent_eadc3334c5d1.md) |
| 10 | `CRWTEMPORARYERROR` | crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP Target.createTarget: WS closed | 6 | 2 | [errors/crwtemporaryerror_0e0cb8a8afc0.md](errors/crwtemporaryerror_0e0cb8a8afc0.md) |
| 11 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (294 bytes, 0 chars visible)) | 6 | 3 | [errors/crw_permanent_f18805dcfe7a.md](errors/crw_permanent_f18805dcfe7a.md) |
| 12 | `CRWTEMPORARYERROR` | crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: No JS renderer available | 5 | 1 | [errors/crwtemporaryerror_a79f27620144.md](errors/crwtemporaryerror_a79f27620144.md) |
| 13 | `CRW_PERMANENT` | Blocked by anti-bot (generic_block): Access Denied on short page (HTTP 403, 111 bytes) | 5 | 1 | [errors/crw_permanent_e699dcbc184f.md](errors/crw_permanent_e699dcbc184f.md) |
| 14 | `DOWNLOAD_HTTP_451` | Download failed with HTTP 451 | 5 | 3 | [errors/download_http_451_096f9dd0432f.md](errors/download_http_451_096f9dd0432f.md) |
| 15 | `CRWTEMPORARYERROR` | crw temporary failure retries exhausted:  | 4 | 1 | [errors/crwtemporaryerror_64239909f895.md](errors/crwtemporaryerror_64239909f895.md) |
| 16 | `CRW_PERMANENT` | Blocked by anti-bot (generic_block): HTTP 403 with HTML content (478 bytes) | 3 | 2 | [errors/crw_permanent_caf33966cc56.md](errors/crw_permanent_caf33966cc56.md) |
| 17 | `CRW_PERMANENT` | No usable content could be extracted (Structural: no <body> tag (1369 bytes)) | 3 | 1 | [errors/crw_permanent_5340c68759b6.md](errors/crw_permanent_5340c68759b6.md) |
| 18 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (686 bytes, 46 chars visible)) | 2 | 2 | [errors/crw_permanent_ccd31177b5c8.md](errors/crw_permanent_ccd31177b5c8.md) |
| 19 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (11537 bytes, 0 chars visible)) | 2 | 2 | [errors/crw_permanent_80e12fcdaf1b.md](errors/crw_permanent_80e12fcdaf1b.md) |
| 20 | `CRW_PERMANENT` | No usable content could be extracted (Structural: no_content_elements, script_heavy_shell (34978 bytes, 63 chars visible)) | 2 | 2 | [errors/crw_permanent_a86e54f70b9b.md](errors/crw_permanent_a86e54f70b9b.md) |
| 21 | `CRW_PERMANENT` | Blocked by anti-bot (generic_block): HTTP 403 with HTML content (146 bytes) | 2 | 1 | [errors/crw_permanent_d6387a8bf0f7.md](errors/crw_permanent_d6387a8bf0f7.md) |
| 22 | `UNSAFEDOWNLOADURL` | Download host could not be resolved | 2 | 2 | [errors/unsafedownloadurl_02464afa77b5.md](errors/unsafedownloadurl_02464afa77b5.md) |
| 23 | `CRW_PERMANENT` | Blocked by anti-bot (generic_block): HTTP 403 with near-empty response (21 bytes) | 1 | 1 | [errors/crw_permanent_d8cf19e979a3.md](errors/crw_permanent_d8cf19e979a3.md) |
| 24 | `CRW_PERMANENT` | No usable content could be extracted (Structural: no <body> tag (1377 bytes)) | 1 | 1 | [errors/crw_permanent_6ccd7348f20d.md](errors/crw_permanent_6ccd7348f20d.md) |
| 25 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (174 bytes, 0 chars visible)) | 1 | 1 | [errors/crw_permanent_0e1a5fa6df52.md](errors/crw_permanent_0e1a5fa6df52.md) |
| 26 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (7877 bytes, 0 chars visible)) | 1 | 1 | [errors/crw_permanent_b3060fa1e58f.md](errors/crw_permanent_b3060fa1e58f.md) |
| 27 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (198 bytes, 0 chars visible)) | 1 | 1 | [errors/crw_permanent_2819ecd2a154.md](errors/crw_permanent_2819ecd2a154.md) |
| 28 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (209 bytes, 0 chars visible)) | 1 | 1 | [errors/crw_permanent_a29a31e014b5.md](errors/crw_permanent_a29a31e014b5.md) |
| 29 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (48023 bytes, 0 chars visible)) | 1 | 1 | [errors/crw_permanent_4edce3ef2cf5.md](errors/crw_permanent_4edce3ef2cf5.md) |
| 30 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (183 bytes, 0 chars visible)) | 1 | 1 | [errors/crw_permanent_cf4e9e9126a8.md](errors/crw_permanent_cf4e9e9126a8.md) |
| 31 | `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text on small page (1485 bytes, 14 chars visible)) | 1 | 1 | [errors/crw_permanent_10db5dd08d76.md](errors/crw_permanent_10db5dd08d76.md) |
| 32 | `DOWNLOAD_HTTP_404` | Download failed with HTTP 404 | 1 | 1 | [errors/download_http_404_6931c8a292e6.md](errors/download_http_404_6931c8a292e6.md) |

## Additional QA findings

### `OUT_OF_SCOPE_URL_LEAK`

**Giải thích:** Crawler đã đưa URL ngoài scope của source vào kết quả. Một số resource URL trả về HTML (`text/html`) nhưng vẫn bị parse link và tiếp tục mở rộng queue; đồng thời navigation allowlist chưa chặn được domain ngoài source.

**Bằng chứng:** Foody job contains external page/resource URLs outside foody.vn; asset URLs returned HTML and exposed external links that could expand the crawl queue.

**Ảnh hưởng:** Crawl có thể thu thập nội dung không liên quan, biến resource thành nguồn phát sinh page/link mới, làm tăng URL expansion và tiêu thụ page/resource budget.

**Khuyến nghị:** Chặn external navigation trước khi enqueue; không parse/follow link từ resource trả HTML; ghi nhận MIME/kind mismatch và canonicalize URL trước khi đưa vào queue.

**Report chi tiết:** [errors/out_of_scope_url_leak_9a0fc4ee81e1.md](errors/out_of_scope_url_leak_9a0fc4ee81e1.md)

### `SOURCE_URL_MISSING_TRAILING_SLASH`

**Giải thích:** Source URL đang thiếu dấu `/` cuối, nên crawler xử lý nó như một path dạng file khi resolve các link tương đối.

**Bằng chứng:** Source `https://docs.pytorch.org/docs/main` tạo ra URL `https://docs.pytorch.org/docs/utils.html` thay vì `https://docs.pytorch.org/docs/main/utils.html`. URL sai trả HTTP 404, trong khi URL hiện hành trả HTTP 200.

**Ảnh hưởng:** Các tài liệu dùng relative link có thể bị chuyển thành đường dẫn sai và bị đánh dấu lỗi. Đây là lỗi xử lý base URL/redirect của crawler, không phải tài liệu PyTorch bị mất.

**Khuyến nghị:** Cấu hình source với dấu `/` cuối hoặc dùng URL version cụ thể; crawler nên resolve link dựa trên `final_url` sau redirect.

**Report chi tiết:** [errors/source_url_missing_trailing_slash_158e3208f479.md](errors/source_url_missing_trailing_slash_158e3208f479.md)


## Crawl runs

| Job ID | Source ID | Classification | Observed pages | Failed pages | Generated |
|---|---|---|---:|---:|---|
| `49ddbae0-3320-4d15-9ffa-eeaf69099d68` | `c306f333-5aaa-4325-abea-9ab2c276bdec` | `RENDERER_INFRASTRUCTURE_FAILURE` | 21200 | 592 | `2026-09-18T05:01:40.972729+00:00` |
| `c5a658df-6d8d-45ef-bfc8-3ccb9e8b1773` | `30d6118e-da6e-49cc-baa6-b4b29abeaaa8` | `RENDERER_INFRASTRUCTURE_FAILURE` | 108 | 80 | `2026-09-18T04:01:57.026920+00:00` |
| `d61f29db-0079-46dd-82c5-23a159f8ea17` | `c306f333-5aaa-4325-abea-9ab2c276bdec` | `MIXED_FAILURE` | 17574 | 87 | `2026-09-18T04:01:00.995416+00:00` |
| `682cc920-4323-4469-87f5-ef2200c89097` | `76c5c3c9-faa5-4dd8-bd64-2794d78723fe` | `NO_FAILURES` | 21 | 0 | `2026-09-18T04:00:27.155743+00:00` |
| `7958f96e-37d1-463d-b6e3-6374b988fe7a` | `76c5c3c9-faa5-4dd8-bd64-2794d78723fe` | `SYSTEMIC_FAILURE` | 42 | 1 | `2026-09-18T04:00:26.790205+00:00` |
| `e8e5c6ad-27f8-4585-83d2-ac9423d1cc47` | `c306f333-5aaa-4325-abea-9ab2c276bdec` | `MIXED_FAILURE` | 3200 | 57 | `2026-09-18T04:00:26.376890+00:00` |
| `656ec477-a92f-41ef-bda5-ee9374eaa156` | `30d6118e-da6e-49cc-baa6-b4b29abeaaa8` | `RENDERER_INFRASTRUCTURE_FAILURE` | 108 | 80 | `2026-09-18T03:59:10.642495+00:00` |

## How to use

- Open the linked detail report for the full evidence and affected page list.
- Send this file together with the relevant detail reports to crawler developers.
- Counts are deduplicated by job ID when the same job is reported again.

<!-- CRAWLER_ERROR_HISTORY_BEGIN
{
  "findings": [
    {
      "answer": "The current document URL returns HTTP 200, but the crawler has 1 matching candidate URL(s) that resolve to 404. The source URL is missing a trailing slash, so a relative document link can resolve against the wrong directory.",
      "code": "SOURCE_URL_MISSING_TRAILING_SLASH",
      "count": 1,
      "detail_path": "errors/source_url_missing_trailing_slash_158e3208f479.md",
      "evidence": [
        {
          "crawler_status_code": null,
          "crawler_url": "https://docs.pytorch.org/docs/utils.html",
          "page_id": "a9e7dd36-5934-42d7-be13-ff0db2cd2abc",
          "probe_error": null,
          "upstream_content_type": "text/html; charset=utf-8",
          "upstream_final_url": "https://docs.pytorch.org/docs/utils.html",
          "upstream_status_code": 404
        }
      ],
      "generated_at": "2026-09-18T04:01:57.026920+00:00",
      "job_id": "c5a658df-6d8d-45ef-bfc8-3ccb9e8b1773",
      "message": "Relative links resolve against a source URL without a trailing slash",
      "metrics": {
        "candidate_count": 1,
        "crawler_404_count": 0,
        "crawler_page_count": 108,
        "expected_content_type": "text/html; charset=utf-8",
        "expected_final_url": "https://docs.pytorch.org/docs/2.14/utils.html",
        "expected_status_code": 200,
        "expected_url": "https://docs.pytorch.org/docs/2.14/utils.html",
        "job_id": "c5a658df-6d8d-45ef-bfc8-3ccb9e8b1773",
        "mismatch_count": 1,
        "probed_candidate_count": 1,
        "relative_link_root_cause": "SOURCE_URL_MISSING_TRAILING_SLASH",
        "relative_resolution_with_slash": "https://docs.pytorch.org/docs/main/utils.html",
        "relative_resolution_without_slash": "https://docs.pytorch.org/docs/utils.html",
        "source_url": "https://docs.pytorch.org/docs/main",
        "source_url_has_trailing_slash": false,
        "upstream_404_count": 1
      },
      "signature": "158e3208f479",
      "source_id": "30d6118e-da6e-49cc-baa6-b4b29abeaaa8"
    },
    {
      "answer": "Foody job contains external page/resource URLs outside foody.vn; asset URLs returned HTML and exposed external links that could expand the crawl queue.",
      "code": "OUT_OF_SCOPE_URL_LEAK",
      "count": 1,
      "detail_path": "errors/out_of_scope_url_leak_9a0fc4ee81e1.md",
      "evidence": [
        {
          "out_of_scope_link_count": 12885,
          "out_of_scope_page_count": 5000,
          "sample_count": 5000,
          "scope_domains": [
            "foody.vn"
          ]
        },
        {
          "asset_url_returning_html_count": 4854,
          "external_domains": {
            "answers.microsoft.com": 1127,
            "domains.google.com": 3873
          },
          "html_resource_with_links_count": 4854,
          "url_path_expansion_count": 5000
        },
        {
          "content_type": "text/html",
          "kind": "RESOURCE",
          "title": "Microsoft Q&A | Microsoft Learn",
          "url": "https://answers.microsoft.com/en-us/media/qna/hero/media/.../logo-entra.png",
          "warning": "redirected_to: https://learn.microsoft.com/en-us/answers/"
        },
        {
          "out_of_scope_links": [
            "https://go.microsoft.com/fwlink/p?LinkID=2092881",
            "https://support.microsoft.com/en-us/teams",
            "https://abs.twimg.com/favicons/twitter.3.ico"
          ]
        }
      ],
      "generated_at": "2026-09-18T05:01:40.972729+00:00",
      "job_id": "49ddbae0-3320-4d15-9ffa-eeaf69099d68",
      "message": "Foody job contains external page/resource URLs outside foody.vn; asset URLs returned HTML and exposed external links that could expand the crawl queue.",
      "metrics": {
        "asset_url_returning_html_count": 4854,
        "finding_code": "OUT_OF_SCOPE_URL_LEAK",
        "html_resource_with_links_count": 4854,
        "job_id": "49ddbae0-3320-4d15-9ffa-eeaf69099d68",
        "mismatch_count": 1,
        "out_of_scope_link_count": 12885,
        "out_of_scope_page_count": 5000,
        "sample_count": 5000,
        "scope_domains": [
          "foody.vn"
        ],
        "url_path_expansion_count": 5000
      },
      "signature": "9a0fc4ee81e1",
      "source_id": "c306f333-5aaa-4325-abea-9ab2c276bdec"
    }
  ],
  "runs": [
    {
      "classification": "RENDERER_INFRASTRUCTURE_FAILURE",
      "error_groups": [
        {
          "code": "CRW_PERMANENT",
          "count": 43,
          "detail_path": "errors/crw_permanent_3b1a353a482c.md",
          "message": "js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed",
          "signature": "3b1a353a482c"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 37,
          "detail_path": "errors/crw_permanent_2ba5aa22751c.md",
          "message": "js_escalation_failed: Renderer error: CDP discovery failed: error sending request",
          "signature": "2ba5aa22751c"
        }
      ],
      "failed_count": 80,
      "generated_at": "2026-09-18T03:59:10.642495+00:00",
      "job_id": "656ec477-a92f-41ef-bda5-ee9374eaa156",
      "observed_page_count": 108,
      "source_id": "30d6118e-da6e-49cc-baa6-b4b29abeaaa8"
    },
    {
      "classification": "MIXED_FAILURE",
      "error_groups": [
        {
          "code": "CRW_PERMANENT",
          "count": 17,
          "detail_path": "errors/crw_permanent_3b1a353a482c.md",
          "message": "js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed",
          "signature": "3b1a353a482c"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 12,
          "detail_path": "errors/crw_permanent_2ba5aa22751c.md",
          "message": "js_escalation_failed: Renderer error: CDP discovery failed: error sending request",
          "signature": "2ba5aa22751c"
        },
        {
          "code": "CRWTEMPORARYERROR",
          "count": 6,
          "detail_path": "errors/crwtemporaryerror_0e0158cf0817.md",
          "message": "crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP discovery failed: error sending request",
          "signature": "0e0158cf0817"
        },
        {
          "code": "UNSAFEDOWNLOADURL",
          "count": 1,
          "detail_path": "errors/unsafedownloadurl_a370df1de898.md",
          "message": "Connected peer differs from the validated DNS result",
          "signature": "a370df1de898"
        },
        {
          "code": "DOWNLOAD_HTTP_451",
          "count": 2,
          "detail_path": "errors/download_http_451_096f9dd0432f.md",
          "message": "Download failed with HTTP 451",
          "signature": "096f9dd0432f"
        },
        {
          "code": "CRWTEMPORARYERROR",
          "count": 4,
          "detail_path": "errors/crwtemporaryerror_0e0cb8a8afc0.md",
          "message": "crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP Target.createTarget: WS closed",
          "signature": "0e0cb8a8afc0"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_ccd31177b5c8.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (686 bytes, 46 chars visible))",
          "signature": "ccd31177b5c8"
        },
        {
          "code": "CRWTEMPORARYERROR",
          "count": 4,
          "detail_path": "errors/crwtemporaryerror_64239909f895.md",
          "message": "crw temporary failure retries exhausted: ",
          "signature": "64239909f895"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_d8cf19e979a3.md",
          "message": "Blocked by anti-bot (generic_block): HTTP 403 with near-empty response (21 bytes)",
          "signature": "d8cf19e979a3"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_6ccd7348f20d.md",
          "message": "No usable content could be extracted (Structural: no <body> tag (1377 bytes))",
          "signature": "6ccd7348f20d"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 3,
          "detail_path": "errors/crw_permanent_ddabd5c2027f.md",
          "message": "Target returned 400 Bad Request",
          "signature": "ddabd5c2027f"
        },
        {
          "code": "UNSAFE_TARGET_URL",
          "count": 1,
          "detail_path": "errors/unsafe_target_url_b1ec305ad5b4.md",
          "message": "Download host could not be resolved (add the host to ssrf_allowed_hosts if this is intended)",
          "signature": "b1ec305ad5b4"
        },
        {
          "code": "DOWNLOAD_HTTP_404",
          "count": 1,
          "detail_path": "errors/download_http_404_6931c8a292e6.md",
          "message": "Download failed with HTTP 404",
          "signature": "6931c8a292e6"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_caf33966cc56.md",
          "message": "Blocked by anti-bot (generic_block): HTTP 403 with HTML content (478 bytes)",
          "signature": "caf33966cc56"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_f18805dcfe7a.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (294 bytes, 0 chars visible))",
          "signature": "f18805dcfe7a"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_80e12fcdaf1b.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (11537 bytes, 0 chars visible))",
          "signature": "80e12fcdaf1b"
        }
      ],
      "failed_count": 57,
      "generated_at": "2026-09-18T04:00:26.376890+00:00",
      "job_id": "e8e5c6ad-27f8-4585-83d2-ac9423d1cc47",
      "observed_page_count": 3200,
      "source_id": "c306f333-5aaa-4325-abea-9ab2c276bdec"
    },
    {
      "classification": "SYSTEMIC_FAILURE",
      "error_groups": [
        {
          "code": "UNSAFE_TARGET_URL",
          "count": 1,
          "detail_path": "errors/unsafe_target_url_b1ec305ad5b4.md",
          "message": "Download host could not be resolved (add the host to ssrf_allowed_hosts if this is intended)",
          "signature": "b1ec305ad5b4"
        }
      ],
      "failed_count": 1,
      "generated_at": "2026-09-18T04:00:26.790205+00:00",
      "job_id": "7958f96e-37d1-463d-b6e3-6374b988fe7a",
      "observed_page_count": 42,
      "source_id": "76c5c3c9-faa5-4dd8-bd64-2794d78723fe"
    },
    {
      "classification": "NO_FAILURES",
      "error_groups": [],
      "failed_count": 0,
      "generated_at": "2026-09-18T04:00:27.155743+00:00",
      "job_id": "682cc920-4323-4469-87f5-ef2200c89097",
      "observed_page_count": 21,
      "source_id": "76c5c3c9-faa5-4dd8-bd64-2794d78723fe"
    },
    {
      "classification": "MIXED_FAILURE",
      "error_groups": [
        {
          "code": "NO_PROXY_AVAILABLE",
          "count": 38,
          "detail_path": "errors/no_proxy_available_2e5558325302.md",
          "message": "HTTP_403",
          "signature": "2e5558325302"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_0e1a5fa6df52.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (174 bytes, 0 chars visible))",
          "signature": "0e1a5fa6df52"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_b3060fa1e58f.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (7877 bytes, 0 chars visible))",
          "signature": "b3060fa1e58f"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 5,
          "detail_path": "errors/crw_permanent_eadc3334c5d1.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (2897 bytes, 46 chars visible))",
          "signature": "eadc3334c5d1"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_2819ecd2a154.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (198 bytes, 0 chars visible))",
          "signature": "2819ecd2a154"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_a29a31e014b5.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (209 bytes, 0 chars visible))",
          "signature": "a29a31e014b5"
        },
        {
          "code": "DOWNLOAD_HTTP_451",
          "count": 2,
          "detail_path": "errors/download_http_451_096f9dd0432f.md",
          "message": "Download failed with HTTP 451",
          "signature": "096f9dd0432f"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 12,
          "detail_path": "errors/crw_permanent_2ba5aa22751c.md",
          "message": "js_escalation_failed: Renderer error: CDP discovery failed: error sending request",
          "signature": "2ba5aa22751c"
        },
        {
          "code": "UNSAFEDOWNLOADURL",
          "count": 2,
          "detail_path": "errors/unsafedownloadurl_a370df1de898.md",
          "message": "Connected peer differs from the validated DNS result",
          "signature": "a370df1de898"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 3,
          "detail_path": "errors/crw_permanent_f18805dcfe7a.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (294 bytes, 0 chars visible))",
          "signature": "f18805dcfe7a"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 5,
          "detail_path": "errors/crw_permanent_e699dcbc184f.md",
          "message": "Blocked by anti-bot (generic_block): Access Denied on short page (HTTP 403, 111 bytes)",
          "signature": "e699dcbc184f"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 6,
          "detail_path": "errors/crw_permanent_ddabd5c2027f.md",
          "message": "Target returned 400 Bad Request",
          "signature": "ddabd5c2027f"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 3,
          "detail_path": "errors/crw_permanent_5340c68759b6.md",
          "message": "No usable content could be extracted (Structural: no <body> tag (1369 bytes))",
          "signature": "5340c68759b6"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_3b1a353a482c.md",
          "message": "js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed",
          "signature": "3b1a353a482c"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_ccd31177b5c8.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (686 bytes, 46 chars visible))",
          "signature": "ccd31177b5c8"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_a86e54f70b9b.md",
          "message": "No usable content could be extracted (Structural: no_content_elements, script_heavy_shell (34978 bytes, 63 chars visible))",
          "signature": "a86e54f70b9b"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_4edce3ef2cf5.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (48023 bytes, 0 chars visible))",
          "signature": "4edce3ef2cf5"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_cf4e9e9126a8.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (183 bytes, 0 chars visible))",
          "signature": "cf4e9e9126a8"
        },
        {
          "code": "UNSAFEDOWNLOADURL",
          "count": 1,
          "detail_path": "errors/unsafedownloadurl_02464afa77b5.md",
          "message": "Download host could not be resolved",
          "signature": "02464afa77b5"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_80e12fcdaf1b.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (11537 bytes, 0 chars visible))",
          "signature": "80e12fcdaf1b"
        }
      ],
      "failed_count": 87,
      "generated_at": "2026-09-18T04:01:00.995416+00:00",
      "job_id": "d61f29db-0079-46dd-82c5-23a159f8ea17",
      "observed_page_count": 17574,
      "source_id": "c306f333-5aaa-4325-abea-9ab2c276bdec"
    },
    {
      "classification": "RENDERER_INFRASTRUCTURE_FAILURE",
      "error_groups": [
        {
          "code": "CRW_PERMANENT",
          "count": 32,
          "detail_path": "errors/crw_permanent_2ba5aa22751c.md",
          "message": "js_escalation_failed: Renderer error: CDP discovery failed: error sending request",
          "signature": "2ba5aa22751c"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 48,
          "detail_path": "errors/crw_permanent_3b1a353a482c.md",
          "message": "js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed",
          "signature": "3b1a353a482c"
        }
      ],
      "failed_count": 80,
      "generated_at": "2026-09-18T04:01:57.026920+00:00",
      "job_id": "c5a658df-6d8d-45ef-bfc8-3ccb9e8b1773",
      "observed_page_count": 108,
      "source_id": "30d6118e-da6e-49cc-baa6-b4b29abeaaa8"
    },
    {
      "classification": "RENDERER_INFRASTRUCTURE_FAILURE",
      "error_groups": [
        {
          "code": "CRW_PERMANENT",
          "count": 206,
          "detail_path": "errors/crw_permanent_3b1a353a482c.md",
          "message": "js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed",
          "signature": "3b1a353a482c"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 188,
          "detail_path": "errors/crw_permanent_b1e9c9438157.md",
          "message": "js_escalation_failed: Renderer error: No JS renderer available",
          "signature": "b1e9c9438157"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 160,
          "detail_path": "errors/crw_permanent_2ba5aa22751c.md",
          "message": "js_escalation_failed: Renderer error: CDP discovery failed: error sending request",
          "signature": "2ba5aa22751c"
        },
        {
          "code": "UNSAFE_TARGET_URL",
          "count": 7,
          "detail_path": "errors/unsafe_target_url_b1ec305ad5b4.md",
          "message": "Download host could not be resolved (add the host to ssrf_allowed_hosts if this is intended)",
          "signature": "b1ec305ad5b4"
        },
        {
          "code": "UNSAFEDOWNLOADURL",
          "count": 1,
          "detail_path": "errors/unsafedownloadurl_02464afa77b5.md",
          "message": "Download host could not be resolved",
          "signature": "02464afa77b5"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 2,
          "detail_path": "errors/crw_permanent_eadc3334c5d1.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (2897 bytes, 46 chars visible))",
          "signature": "eadc3334c5d1"
        },
        {
          "code": "UNSAFEDOWNLOADURL",
          "count": 7,
          "detail_path": "errors/unsafedownloadurl_a370df1de898.md",
          "message": "Connected peer differs from the validated DNS result",
          "signature": "a370df1de898"
        },
        {
          "code": "CRWTEMPORARYERROR",
          "count": 5,
          "detail_path": "errors/crwtemporaryerror_0e0158cf0817.md",
          "message": "crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP discovery failed: error sending request",
          "signature": "0e0158cf0817"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_10db5dd08d76.md",
          "message": "No usable content could be extracted (Structural: minimal_text on small page (1485 bytes, 14 chars visible))",
          "signature": "10db5dd08d76"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 2,
          "detail_path": "errors/crw_permanent_d6387a8bf0f7.md",
          "message": "Blocked by anti-bot (generic_block): HTTP 403 with HTML content (146 bytes)",
          "signature": "d6387a8bf0f7"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 1,
          "detail_path": "errors/crw_permanent_a86e54f70b9b.md",
          "message": "No usable content could be extracted (Structural: no_content_elements, script_heavy_shell (34978 bytes, 63 chars visible))",
          "signature": "a86e54f70b9b"
        },
        {
          "code": "CRWTEMPORARYERROR",
          "count": 5,
          "detail_path": "errors/crwtemporaryerror_a79f27620144.md",
          "message": "crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: No JS renderer available",
          "signature": "a79f27620144"
        },
        {
          "code": "CRWTEMPORARYERROR",
          "count": 2,
          "detail_path": "errors/crwtemporaryerror_0e0cb8a8afc0.md",
          "message": "crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP Target.createTarget: WS closed",
          "signature": "0e0cb8a8afc0"
        },
        {
          "code": "DOWNLOAD_HTTP_451",
          "count": 1,
          "detail_path": "errors/download_http_451_096f9dd0432f.md",
          "message": "Download failed with HTTP 451",
          "signature": "096f9dd0432f"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 2,
          "detail_path": "errors/crw_permanent_caf33966cc56.md",
          "message": "Blocked by anti-bot (generic_block): HTTP 403 with HTML content (478 bytes)",
          "signature": "caf33966cc56"
        },
        {
          "code": "CRW_PERMANENT",
          "count": 2,
          "detail_path": "errors/crw_permanent_f18805dcfe7a.md",
          "message": "No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (294 bytes, 0 chars visible))",
          "signature": "f18805dcfe7a"
        }
      ],
      "failed_count": 592,
      "generated_at": "2026-09-18T05:01:40.972729+00:00",
      "job_id": "49ddbae0-3320-4d15-9ffa-eeaf69099d68",
      "observed_page_count": 21200,
      "source_id": "c306f333-5aaa-4325-abea-9ab2c276bdec"
    }
  ]
}
CRAWLER_ERROR_HISTORY_END -->
