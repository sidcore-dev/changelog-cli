import io
import os
import subprocess
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from changelog_cli.cli import main


def _git(args: list[str], cwd: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _init_repo(path: str) -> None:
    _git(["init", "-q", "-b", "main"], path)
    _git(["config", "user.email", "test@example.com"], path)
    _git(["config", "user.name", "Test User"], path)


def _commit(path: str, filename: str, message: str) -> None:
    Path(path, filename).write_text(message)
    _git(["add", filename], path)
    _git(["commit", "-q", "-m", message], path)


class TestCli(unittest.TestCase):
    def _run_in(self, path: str, argv: list[str]):
        cwd = os.getcwd()
        os.chdir(path)
        try:
            out = io.StringIO()
            with redirect_stdout(out):
                code = main(argv)
            return code, out.getvalue()
        finally:
            os.chdir(cwd)

    def test_not_a_git_repo_returns_1(self) -> None:
        with TemporaryDirectory() as tmp:
            code, _ = self._run_in(tmp, [])
            self.assertEqual(code, 1)

    def test_generates_changelog_grouped_by_type(self) -> None:
        with TemporaryDirectory() as tmp:
            _init_repo(tmp)
            _commit(tmp, "a.txt", "feat: add widget")
            _commit(tmp, "b.txt", "fix: correct typo")
            code, out = self._run_in(tmp, [])
            self.assertEqual(code, 0)
            self.assertIn("### Features", out)
            self.assertIn("add widget", out)
            self.assertIn("### Bug Fixes", out)
            self.assertIn("correct typo", out)

    def test_from_and_to_refs(self) -> None:
        with TemporaryDirectory() as tmp:
            _init_repo(tmp)
            _commit(tmp, "a.txt", "feat: first")
            _git(["tag", "v1.0.0"], tmp)
            _commit(tmp, "b.txt", "feat: second")
            code, out = self._run_in(tmp, ["--from", "v1.0.0", "--to", "HEAD"])
            self.assertEqual(code, 0)
            self.assertIn("second", out)
            self.assertNotIn("first", out)

    def test_defaults_to_most_recent_tag(self) -> None:
        with TemporaryDirectory() as tmp:
            _init_repo(tmp)
            _commit(tmp, "a.txt", "feat: first")
            _git(["tag", "v1.0.0"], tmp)
            _commit(tmp, "b.txt", "feat: second")
            code, out = self._run_in(tmp, [])
            self.assertEqual(code, 0)
            self.assertIn("v1.0.0", out)
            self.assertIn("second", out)
            self.assertNotIn("first", out)

    def test_no_tags_lists_full_history(self) -> None:
        with TemporaryDirectory() as tmp:
            _init_repo(tmp)
            _commit(tmp, "a.txt", "feat: only commit")
            code, out = self._run_in(tmp, [])
            self.assertEqual(code, 0)
            self.assertIn("only commit", out)
            self.assertIn("Changes through HEAD", out)


if __name__ == "__main__":
    unittest.main()
