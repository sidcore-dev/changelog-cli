# changelog-cli

A small, dependency-free command-line tool that generates a Markdown
changelog section from your git commit history, grouping commits by
their [Conventional Commits](https://www.conventionalcommits.org/) type.

## Why

Writing a changelog by hand means re-reading every commit message and
manually sorting it into "features" vs "fixes" vs "everything else."
If your commits already follow `feat:`/`fix:`/`docs:` conventions,
`changelog-cli` does that sorting for you and prints ready-to-paste
Markdown.

## Install

```bash
pip install .
```

This installs a `changelog-cli` command on your PATH. It shells out to
`git`, so `git` must be installed and the command must be run inside a
git repository.

## Usage

```bash
changelog-cli
```

By default this generates a changelog from the most recent tag (if any)
to `HEAD`. Example output:

```
## Changes from v1.2.0 to HEAD

### Features

- add dark mode toggle
- support CSV export

### Bug Fixes

- correct off-by-one error in pagination

### Other

- bump version to 1.3.0
```

Specify an explicit range:

```bash
changelog-cli --from v1.0.0 --to v1.1.0
```

### Options

| Flag       | Description                                              |
|------------|------------------------------------------------------------|
| `--from`   | Starting ref (default: most recent tag, if any)             |
| `--to`     | Ending ref (default: `HEAD`)                                 |

### Exit codes

- `0` — changelog generated successfully
- `1` — not run inside a git repository, or the given refs are invalid
- `2` — `git` is not installed or not on `PATH`

## Development

```bash
pip install -e .
python -m unittest discover -s tests -v
```

## License

All rights reserved. This code is public for viewing and reference only —
no license is granted to use, copy, modify, or redistribute it. See
[LICENSE](LICENSE) for details.
