# Contributing to AutoIntel (Price-My-Car)

Thanks for your interest in AutoIntel! Bug reports, documentation, and pull requests are welcome.

## Getting started

1. Fork the repository and clone your fork.
2. Create a feature branch: `git checkout -b feature/amazing`.
3. Install dependencies: `pip install -r requirements.txt`.

## Development workflow

- Add or update tests for every change.
- Run the test suite: `pytest tests/test_helpers.py` (65 unit tests).
- Verify the app boots: `streamlit run app/streamlit_app.py` (demo credentials: `demo` / `demo123`).
- Keep non-UI logic in `app/helpers.py` so it stays testable without Streamlit.

## Commit conventions

Keep commits small and focused. Prefix messages with a type, e.g. `feat:`, `fix:`, `docs:`, `test:`.

## Opening a pull request

1. Push your branch and open a PR against `main`.
2. Describe what you changed and why.
3. Link any related issue.

By contributing, you agree that your contributions are licensed under the MIT License.
