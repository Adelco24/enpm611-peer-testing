import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import config
from model import Issue

from labels_analysis import LabelsAnalysis
from state_analysis import StateAnalysis
from example_analysis import ExampleAnalysis


def make_issue(
    number,
    creator,
    labels,
    state="open",
    created_date="2024-09-01T00:00:00+00:00",
    updated_date="2024-09-02T00:00:00+00:00",
    events=None
):
    return Issue({
        "url": f"https://github.com/example/project/issues/{number}",
        "creator": creator,
        "labels": labels,
        "state": state,
        "assignees": [],
        "title": f"Issue {number}",
        "text": "Body",
        "number": number,
        "created_date": created_date,
        "updated_date": updated_date,
        "timeline_url": "timeline",
        "events": events or []
    })


class FakeDataLoader:
    def __init__(self, issues):
        self.issues = issues

    def get_issues(self):
        return self.issues


class TestAnalyses(unittest.TestCase):

    def setUp(self):
        config._config = {}
        self.issues = [
            make_issue(
                1,
                "alice",
                ["Bug", "Needs Triage"],
                "open",
                events=[
                    {
                        "event_type": "labeled",
                        "author": "alice",
                        "event_date": "2024-09-01T00:01:00+00:00",
                        "label": "Bug"
                    },
                    {
                        "event_type": "commented",
                        "author": "bob",
                        "event_date": "2024-09-01T00:02:00+00:00",
                        "comment": "comment"
                    }
                ]
            ),
            make_issue(
                2,
                "bob",
                ["Documentation"],
                "closed",
                "2024-10-01T00:00:00+00:00",
                "2024-10-03T00:00:00+00:00",
                events=[
                    {
                        "event_type": "closed",
                        "author": "bob",
                        "event_date": "2024-10-03T00:00:00+00:00"
                    }
                ]
            ),
            make_issue(
                3,
                "alice",
                ["Bug"],
                "closed",
                "2024-11-01T00:00:00+00:00",
                "2024-11-02T00:00:00+00:00",
                events=[]
            )
        ]

    def tearDown(self):
        config._config = {}

    @patch("labels_analysis.plt.show")
    @patch("labels_analysis.DataLoader")
    def test_labels_analysis_all_labels(self, mock_loader_class, mock_show):
        mock_loader_class.return_value = FakeDataLoader(self.issues)
        config._config = {"label": None}

        output = io.StringIO()
        with redirect_stdout(output):
            LabelsAnalysis().run()

        text = output.getvalue()
        self.assertIn("Label statistics", text)
        self.assertIn("Bug average time to close", text)
        self.assertIn("Bug found in 2 issues", text)
        self.assertTrue(mock_show.called)

    @patch("labels_analysis.DataLoader")
    def test_labels_analysis_specific_existing_label(self, mock_loader_class):
        mock_loader_class.return_value = FakeDataLoader(self.issues)
        config._config = {"label": "Bug"}

        output = io.StringIO()
        with redirect_stdout(output):
            LabelsAnalysis().run()

        text = output.getvalue()
        self.assertIn("Bug average time to close", text)
        self.assertIn("Bug found in 2 issues", text)

    @patch("labels_analysis.DataLoader")
    def test_labels_analysis_missing_label(self, mock_loader_class):
        mock_loader_class.return_value = FakeDataLoader(self.issues)
        config._config = {"label": "NoSuchLabel"}

        output = io.StringIO()
        with redirect_stdout(output):
            LabelsAnalysis().run()

        self.assertIn('Label "NoSuchLabel" does not exist in issues', output.getvalue())

    @patch("state_analysis.DataLoader")
    def test_state_analysis_open_and_closed(self, mock_loader_class):
        mock_loader_class.return_value = FakeDataLoader(self.issues)

        output = io.StringIO()
        with redirect_stdout(output):
            StateAnalysis().run()

        text = output.getvalue()
        self.assertIn("Found 3 issues", text)
        self.assertIn("open", text)
        self.assertIn("closed", text)
        self.assertIn("Top contributor: alice", text)
        self.assertIn("alice: 1", text)

    @patch("state_analysis.DataLoader")
    def test_state_analysis_no_open_users(self, mock_loader_class):
        closed_only = [
            make_issue(4, "dave", ["Bug"], "closed"),
            make_issue(5, "erin", ["Documentation"], "closed")
        ]
        mock_loader_class.return_value = FakeDataLoader(closed_only)

        output = io.StringIO()
        with redirect_stdout(output):
            StateAnalysis().run()

        text = output.getvalue()
        self.assertIn("Found 2 issues", text)
        self.assertIn("No users with open issues", text)

    @patch("example_analysis.plt.show")
    @patch("example_analysis.DataLoader")
    def test_example_analysis_all_users(self, mock_loader_class, mock_show):
        mock_loader_class.return_value = FakeDataLoader(self.issues)
        config._config = {"user": None}

        output = io.StringIO()
        with redirect_stdout(output):
            ExampleAnalysis().run()

        text = output.getvalue()
        self.assertIn("Found 3 events across 3 issues", text)
        self.assertTrue(mock_show.called)

    @patch("example_analysis.plt.show")
    @patch("example_analysis.DataLoader")
    def test_example_analysis_specific_user(self, mock_loader_class, mock_show):
        mock_loader_class.return_value = FakeDataLoader(self.issues)
        config._config = {"user": "bob"}

        output = io.StringIO()
        with redirect_stdout(output):
            ExampleAnalysis().run()

        text = output.getvalue()
        self.assertIn("Found 2 events across 3 issues for bob", text)
        self.assertTrue(mock_show.called)


if __name__ == "__main__":
    unittest.main()
