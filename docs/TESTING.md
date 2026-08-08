# Testing Strategy & Contracts

## TDD Workflow

All domain rules and storage operations follow the TDD loop:

```
1. Write failing test in tests/unit/ (Red)
2. Run `pytest` to confirm failure
3. Implement minimal code in src/phase_annotator/ (Green)
4. Run `pytest` to confirm pass
5. Refactor code & tests cleanly
```

## Running Tests

```bash
# Run all unit tests
pytest -v tests/unit/

# Run all integration tests
pytest -v tests/integration/

# Run complete suite
pytest -v tests/
```

## Testing Contracts

1. **No GUI in Unit Tests**: Domain unit tests must never instantiate Qt widgets or depend on display servers.
2. **Deterministic Inputs**: Tests must use fixed timestamps/frames and mock video metadata.
3. **Storage Isolation**: Storage tests must use temporary directories (`tmp_path` fixture) to isolate file IO.
