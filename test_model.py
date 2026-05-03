import unittest

from model import Event, Issue, State


class TestModel(unittest.TestCase):

    def test_event_from_valid_json(self):
        data = {
            "event_type": "commented",
            "author": "alice",
            "event_date": "2024-09-25T14:42:51+00:00",
            "label": "Bug",
            "comment": "This is a test comment"
        }

        event = Event(data)

        self.assertEqual(event.event_type, "commented")
        self.assertEqual(event.author, "alice")
        self.assertEqual(event.label, "Bug")
        self.assertEqual(event.comment, "This is a test comment")
        self.assertIsNotNone(event.event_date)

    def test_event_handles_missing_and_bad_date(self):
        data = {
            "event_type": "labeled",
            "author": "bob",
            "event_date": "not-a-date"
        }

        event = Event(data)

        self.assertEqual(event.event_type, "labeled")
        self.assertEqual(event.author, "bob")
        self.assertIsNone(event.event_date)
        self.assertIsNone(event.label)
        self.assertIsNone(event.comment)

    def test_issue_from_valid_json(self):
        data = {
            "url": "https://github.com/example/project/issues/1",
            "creator": "alice",
            "labels": ["Bug", "Needs Triage"],
            "state": "open",
            "assignees": ["bob"],
            "title": "Example issue",
            "text": "Issue body text",
            "number": "1",
            "created_date": "2024-09-25T14:42:51+00:00",
            "updated_date": "2024-09-25T15:42:51+00:00",
            "timeline_url": "https://api.github.com/example/timeline",
            "events": [
                {
                    "event_type": "commented",
                    "author": "bob",
                    "event_date": "2024-09-25T15:00:00+00:00",
                    "comment": "hello"
                }
            ]
        }

        issue = Issue(data)

        self.assertEqual(issue.url, data["url"])
        self.assertEqual(issue.creator, "alice")
        self.assertEqual(issue.labels, ["Bug", "Needs Triage"])
        self.assertEqual(issue.state, State.open)
        self.assertEqual(issue.assignees, ["bob"])
        self.assertEqual(issue.title, "Example issue")
        self.assertEqual(issue.text, "Issue body text")
        self.assertEqual(issue.number, 1)
        self.assertIsNotNone(issue.created_date)
        self.assertIsNotNone(issue.updated_date)
        self.assertEqual(issue.timeline_url, data["timeline_url"])
        self.assertEqual(len(issue.events), 1)
        self.assertEqual(issue.events[0].author, "bob")

    def test_issue_defaults_when_no_json(self):
        issue = Issue()

        self.assertIsNone(issue.url)
        self.assertIsNone(issue.creator)
        self.assertEqual(issue.labels, [])
        self.assertIsNone(issue.state)
        self.assertEqual(issue.assignees, [])
        self.assertEqual(issue.number, -1)
        self.assertEqual(issue.events, [])

    def test_issue_handles_bad_number_and_dates(self):
        data = {
            "url": "url",
            "creator": "alice",
            "labels": [],
            "state": "closed",
            "assignees": [],
            "title": "Bad fields",
            "text": "Body",
            "number": "abc",
            "created_date": "bad-date",
            "updated_date": "also-bad",
            "timeline_url": "timeline",
            "events": []
        }

        issue = Issue(data)

        self.assertEqual(issue.state, State.closed)
        self.assertEqual(issue.number, -1)
        self.assertIsNone(issue.created_date)
        self.assertIsNone(issue.updated_date)
        self.assertEqual(issue.events, [])


if __name__ == "__main__":
    unittest.main()
