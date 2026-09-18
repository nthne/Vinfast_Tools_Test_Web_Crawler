# `diagnose_out_of_scope_urls`

Read-only diagnostic for URLs that escape a source's configured host scope.

It checks both persisted page rows and `metadata.links` because an external URL
can be visible as a discovered link before it is persisted as a page. It also
separates these cases:

- external `NAVIGATION` pages;
- external `RESOURCE` pages;
- asset URLs returning `text/html`;
- HTML resources whose links were parsed and could expand the queue;
- `NAVIGATION` records returning binary/image MIME;
- repeated path segments that indicate URL canonicalization or expansion.

The tool never retries, cancels, deletes, or updates crawler data.
