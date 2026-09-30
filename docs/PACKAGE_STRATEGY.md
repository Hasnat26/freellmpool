# Package and Import Strategy

## Decision

Industrial RFQ Intelligence uses the repository/project identity `industrial-rfq-intelligence`, while the current Python implementation package remains `freellmpool` for backward compatibility.

The package namespace is intentionally **not renamed in this cleanup phase**.

## Why the namespace is retained

The repository still contains a broader legacy provider/router API surface under `src/freellmpool/`. Existing imports, tests, internal modules, console aliases, and provider configuration depend on that namespace.

Renaming the directory directly would create a large compatibility change that is unrelated to the industrial RFQ product identity cleanup. It would also make the current implementation harder to validate incrementally.

## Product-facing identity

Use these names for new documentation and user-facing workflows:

- Repository: `industrial-rfq-intelligence`
- Python distribution: `industrial-rfq-intelligence`
- Primary executable: `industrial-rfq-intelligence`
- Industrial workflow command: `industrial-rfq-intelligence industrial-rfq`

The legacy executable aliases `freellmpool` and `ffp` remain temporarily available.

## Python imports

Current industrial functionality is imported from:

```python
from freellmpool.industrial import build_report
```

This is a compatibility namespace, not the product branding.

## Packaging

The wheel currently packages:

```text
src/freellmpool/
```

and Hatch is configured accordingly in `pyproject.toml`.

This remains unchanged until a dedicated package-migration milestone can cover:

1. a new package namespace;
2. compatibility shims for existing imports;
3. migration of internal relative imports;
4. test and CI migration;
5. package-data migration;
6. a deprecation path for the old namespace;
7. clean wheel/sdist validation.

## Boundary

Do not introduce new public documentation that presents `freellmpool` as the product name.

Do not perform a wholesale package rename merely to remove the legacy namespace. The migration should be a separate, tested compatibility project.

## Current status

This strategy allows the repository to present a coherent Industrial RFQ Intelligence product while preserving the existing Python implementation surface. The next package-identity work should be treated as a controlled migration rather than a string-replacement cleanup.
