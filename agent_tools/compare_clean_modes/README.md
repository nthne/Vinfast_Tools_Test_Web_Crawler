# `compare_clean_modes`

So sánh output và trạng thái của `RAW`, `LIGHT`, `HEAVY`, `SAFE` hoặc các clean mode upstream khác.

Input:

```json
{"page_id": "string", "modes": ["RAW", "LIGHT", "HEAVY", "SAFE"]}
```

Đo original/kept characters, retention ratio, degraded và reverted state.
