import json
import os
import tempfile
import unittest

import config
import data_loader
from data_loader import DataLoader
from model import Issue


class TestDataLoader(unittest.TestCase):

    def setUp(self):
        config._config = {}
        data_loader._ISSUES = None
        os.environ.pop("ENPM611_PROJECT_DATA_PATH", None)

    def tearDown(self):
        config._config = None
        data_loader._ISSUES = None
        os.environ.pop("ENPM611_PROJECT_DATA_PATH", None)

    def test_loads_issues_from_json_file(self):
        sample_data = [
            {
                "url": "https://github.com/example/project/issues/1",
                "creator": "alice",
                "labels": ["Bug"],
                "state": "open",
                "assignees": [],
                "title": "Issue 1",
                "text": "Body",
                "number": 1,
                "created_date": "2024-09-01T00:00:00+00:00",
                "updated_date": "2024-09-02T00:00:00+00:00",
                "timeline_url": "timeline",
                "events": [
                    {
                        "event_type": "labeled",
                        "author": "alice",
                        "event_date": "2024-09-01T00:01:00+00:00",
                        "label": "Bug"
                    }
                ]
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp_file:
            json.dump(sample_data, temp_file)
            temp_path = temp_file.name

        try:
            os.environ["ENPM611_PROJECT_DATA_PATH"] = temp_path

            loader = DataLoader()
            issues = loader.get_issues()

            self.assertEqual(len(issues), 1)
            self.assertIsInstance(issues[0], Issue)
            self.assertEqual(issues[0].creator, "alice")
            self.assertEqual(issues[0].labels, ["Bug"])
            self.assertEqual(len(issues[0].events), 1)
        finally:
            os.remove(temp_path)

    def test_get_issues_uses_cached_singleton(self):
        sample_data = [
            {
                "url": "url",
                "creator": "alice",
                "labels": [],
                "state": "open",
                "assignees": [],
                "title": "Issue",
                "text": "Body",
                "number": 1,
                "created_date": "2024-09-01T00:00:00+00:00",
                "updated_date": "2024-09-01T00:00:00+00:00",
                "timeline_url": "timeline",
                "events": []
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as temp_file:
            json.dump(sample_data, temp_file)
            temp_path = temp_file.name

        try:
            os.environ["ENPM611_PROJECT_DATA_PATH"] = temp_path

            loader = DataLoader()
            first = loader.get_issues()
            second = loader.get_issues()

            self.assertIs(first, second)
            self.assertEqual(len(second), 1)
        finally:
            os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
