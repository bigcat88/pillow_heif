# Contributing to pillow-heif

Bug fixes, feature additions, tests, documentation and more can be contributed via [issues](https://github.com/bigcat88/pillow_heif/issues) and/or [pull requests](https://github.com/bigcat88/pillow_heif/pulls). All contributions are welcome.

## Bug fixes, feature additions, etc.

Please send a pull request to the `master` branch.  Feel free to ask questions [via issues](https://github.com/bigcat88/pillow_heif/issues) or [discussions](https://github.com/bigcat88/pillow_heif/discussions)

- Fork the pillow-heif repository.
- Create a branch from `master`.
- Install dev requirements with `pip install ".[dev]"`
- Develop bug fixes, features, tests, etc.
- Run the test suite. Run `coverage run -m pytest &&  coverage html` to see if the changed code is covered by tests.
- Install `pylint` locally, it will run during `pre-commit`.
- Install `pre-commit` hooks by `pre-commit install` command.
- Create a pull request to pull the changes from your branch to the pillow-heif `master`.

### Guidelines

- Separate code commits from reformatting commits.
- Provide tests for any newly added code.
- Follow PEP 8.
- Update CHANGELOG.md as needed or appropriate with your bug fixes, feature additions and tests.

## Security vulnerabilities

Please see our [security policy](https://github.com/bigcat88/pillow_heif/blob/master/SECURITY.md).
