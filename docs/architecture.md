# Architecture

```text
local export / authenticated crawler API
                 |
          CrawlerClient
                 |
          schema mapper
                 |
           CrawledPage
                 |
        QAEngine + QAContext
                 |
    SQLite scan persistence + exports
                 |
            CLI / FastAPI UI
```

The local file connector is selected by `CRAWLER_DATA_PATH` and supports the supplied Parquet export as well as CSV/JSON. The HTTP connector is selected when `CRAWLER_BASE_URL` is set. Upstream records are never passed directly to rules: `CrawlerPageMapper` is the boundary that absorbs schema differences.

The MVP deliberately keeps the QA pipeline deterministic and explainable. Expensive checks and language/semantic checks are future extension points. A failing page is captured as a page-level result and cannot abort the rest of a source scan.
