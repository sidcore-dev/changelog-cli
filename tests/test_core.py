import unittest

from changelog_cli.core import group_commits, parse_subject, render_changelog


class TestParseSubject(unittest.TestCase):
    def test_feat_prefix(self) -> None:
        self.assertEqual(parse_subject("feat: add login page"), ("Features", "add login page"))

    def test_fix_with_scope(self) -> None:
        self.assertEqual(parse_subject("fix(auth): handle expired tokens"), ("Bug Fixes", "handle expired tokens"))

    def test_breaking_change_marker(self) -> None:
        self.assertEqual(parse_subject("feat!: drop legacy API"), ("Features", "drop legacy API"))

    def test_unknown_prefix_falls_back_to_other(self) -> None:
        self.assertEqual(parse_subject("bump version to 2.0"), ("Other", "bump version to 2.0"))

    def test_unrecognized_type_word_falls_back_to_other(self) -> None:
        self.assertEqual(parse_subject("wip: half-finished thing"), ("Other", "wip: half-finished thing"))


class TestGroupCommits(unittest.TestCase):
    def test_groups_by_category(self) -> None:
        groups = group_commits(["feat: a", "fix: b", "feat: c", "random change"])
        self.assertEqual(groups["Features"], ["a", "c"])
        self.assertEqual(groups["Bug Fixes"], ["b"])
        self.assertEqual(groups["Other"], ["random change"])

    def test_skips_blank_subjects(self) -> None:
        groups = group_commits(["feat: a", "", "   "])
        self.assertEqual(groups, {"Features": ["a"]})


class TestRenderChangelog(unittest.TestCase):
    def test_renders_headed_sections_in_order(self) -> None:
        text = render_changelog(["fix: b", "feat: a"], "v1.0.0", "HEAD")
        self.assertIn("## Changes from v1.0.0 to HEAD", text)
        features_pos = text.index("### Features")
        fixes_pos = text.index("### Bug Fixes")
        self.assertLess(features_pos, fixes_pos)
        self.assertIn("- a", text)
        self.assertIn("- b", text)

    def test_no_from_ref_uses_alternate_header(self) -> None:
        text = render_changelog(["feat: a"], None, "HEAD")
        self.assertIn("## Changes through HEAD", text)

    def test_no_commits_message(self) -> None:
        text = render_changelog([], "v1.0.0", "HEAD")
        self.assertIn("No commits found.", text)


if __name__ == "__main__":
    unittest.main()
