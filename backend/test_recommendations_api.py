"""API tests with explicit fake data; no PostgreSQL required."""

import unittest
from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.recommendations import (
    get_recommendation_context,
    router,
)
from app.services.recommendations.context import build_user_context
from app.services.recommendations.fake_sources import FakeSources


class RecommendationAPITests(unittest.TestCase):
    def setUp(self):
        self.sources = FakeSources.from_fixture()
        self.user_id = 1

        self.app = FastAPI()
        self.app.include_router(router)
        self.app.dependency_overrides[
            get_recommendation_context
        ] = self.fake_context

    def fake_context(self):
        return build_user_context(
            db=None,
            user_id=self.user_id,
            sources=self.sources,
            today=date(2026, 11, 4),
        )

    def test_returns_two_cards(self):
        with TestClient(self.app) as client:
            response = client.post("/recommendations/generate")

        self.assertEqual(response.status_code, 200, response.text)
        cards = response.json()["recommendations"]
        self.assertEqual(
            [card["type"] for card in cards],
            ["study", "discovery"],
        )
        for card in cards:
            self.assertGreater(card["estimated_minutes"], 0)
            self.assertTrue(card["id"])
            for item in card["evidence"]:
                self.assertTrue(item["label"])

    def test_empty_user(self):
        self.user_id = 999
        with TestClient(self.app) as client:
            response = client.post("/recommendations/generate")

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), {"recommendations": []})


if __name__ == "__main__":
    unittest.main()