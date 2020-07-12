import json
import requests
import unittest
from run import app, db, Urls, long_url_exist, get_random_text
import re


class TestMyRun(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.Urls = Urls
        self.temp = "http://MVSXX.COMPANY.COM"
        self.client = self.app.test_client()
        self.data = [
            {
                "long_url": "http://MVSXX.COMPANY.COM:04445/CICSPLEXSM//JSMITH/VIEW/OURLOCTRAN?CONTEXT=FRED&SCOPE=FRED&A_TRANID=PAY"
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
            {"long_url": "http://github.com", "exp_date": "2021-2-12"},
            {"long_url": "http://gitlab.com", "exp_date": "2021/02/12"},
            {"long_url": "https://www.manutd.com"},
            {"long_url": "http://sepidroodsc.com", "exp_date": "2212-02-12"},
        ]

    def test_get(self):
        resp = self.client.get(path="/", content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["message"], "Welcome to koojelink!")

    def test_long_url_exist(self):
        temp_q = long_url_exist(self.Urls, self.data[0]["long_url"])
        self.assertTrue(temp_q)
        self.assertEqual(get_random_text(temp_q), "5i7rrY")
        self.assertIsNone(get_random_text(long_url_exist(self.Urls, self.temp)))

    def test_post_wrong(self):
        for i in range(1, 5):
            post = self.client.post(
                path="/", data=json.dumps(self.data[i]), content_type="application/json"
            )
            self.assertEqual(post.status_code, 200)
            self.assertNotIn("https://koojelink/", post.data.decode("utf-8"))
            self.assertEqual(post.json["error"], "wrong key:value input")

    def test_wrong_time_format(self):
        for i in range(5, 7):
            post = self.client.post(
                path="/", data=json.dumps(self.data[i]), content_type="application/json"
            )
            self.assertEqual(
                post.json["error"], "Incorrect data format, should be YYYY-MM-DD"
            )

    def test_post_correct(self):
        for i in range(7, 9):
            post = self.client.post(
                path="/", data=json.dumps(self.data[i]), content_type="application/json"
            )
            temp = long_url_exist(self.Urls, self.data[i]["long_url"])
            if temp:
                self.assertEqual(post.status_code, 200)
                self.assertEqual(
                    post.data.decode("utf-8").split("k/")[1], temp.random_text
                )
            else:
                self.assertEqual(post.status_code, 200)
                self.assertIn("https://koojelink/", post.data.decode("utf-8"))
                self.assertFalse(
                    re.search(
                        r"[^a-zA-Z0-9]+", post.data.decode("utf-8").split("k/")[1]
                    )
                )

    def test_db_update(self):
        long_url_exist(self.Urls, self.data[5]["long_url"])
        for i in range(5, 7):
            self.assertIsNone(long_url_exist(self.Urls, self.data[i]["long_url"]))
        for i in range(7, 9):
            self.assertEqual(
                long_url_exist(self.Urls, self.data[i]["long_url"]).long_url,
                self.data[i]["long_url"],
            )


# if __name__ == "__main__":
#     unittest.main()
