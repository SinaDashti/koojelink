import json
import requests
import unittest
from run import app
import re


class TestMyRun(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.data = [
            {
                "long_url": "http://MVSXX.COMPANY.COM:04445/CICSPLEXSM//JSMITH/VIEW/OURLOCTRAN?CONTEXT=FRED&SCOPE=FRED&A_TRANID=PAY*"
            },
            {
                "long_url": "http:/MVSXX.COMPANY.COM:04445/CICSPLEXSM//JSMITH/MENU/OURHOME?CONTEXT=FRED&SCOPE=FRED"
            },
            {
                "long_url": "http//MVSXX.COMPANY.COM:04445/CICSPLEXSM//JSMITH/MENU/OURHOME?CONTEXT=FRED&SCOPE=FRED"
            },
            {
                "long_url": "htt://MVSXX.COMPANY.COM:04445/CICSPLEXSM//JSMITH/MENU/OURHOME?CONTEXT=FRED&SCOPE=FRED"
            },
            {
                "long_url": "http://MVSXX.COMPANY.COM:04445CICSPLEXSM/JSMITH/MENU//OURHOME?CONTEXT=FRED&SCOPE=FRED"
            },
        ]

    def test_get(self):
        resp = self.client.get(path="/", content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["message"], "Welcome to koojelink!")

    def test_post_correct(self):
        post = self.client.post(
            path="/", data=json.dumps(self.data[0]), content_type="application/json"
        )
        self.assertEqual(post.status_code, 200)
        self.assertIn("https://koojelink/", post.data.decode("utf-8"))
        self.assertFalse(
            re.search(r"[^a-zA-Z0-9]+", post.data.decode("utf-8").split("k/")[1])
        )

    def test_post_wrong(self):
        for i in range(1, 4):
            post = self.client.post(
                path="/", data=json.dumps(self.data[i]), content_type="application/json"
            )
            self.assertEqual(post.status_code, 200)
            self.assertNotIn("https://koojelink/", post.data.decode("utf-8"))
            self.assertEqual(post.json["error"], "wrong key:value input")


if __name__ == "__main__":
    unittest.main()
