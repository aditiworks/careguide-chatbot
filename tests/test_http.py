import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from app import Handler

class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, method="GET", path="/", body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        try:
            conn.request(method, path, body=body, headers=headers or {})
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            conn.close()

    def post(self, data, **overrides):
        headers = {"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{self.port}"}
        headers.update(overrides)
        return self.request("POST", "/api/chat", json.dumps(data), headers)

    def test_static_and_headers(self):
        for path in ["/", "/style.css", "/script.js", "/health"]:
            with self.subTest(path=path):
                status, headers, body = self.request(path=path)
                self.assertEqual(status, 200)
                self.assertTrue(body)
                self.assertEqual(headers["Cache-Control"], "no-store")
                self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_api(self):
        status, _, body = self.post({"message": "chest pain"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["kind"], "emergency")

    def test_payload_validation(self):
        for data in [None, [], {}, {"message": 1}, {"message": ""}, {"message": "x"*2001}]:
            with self.subTest(data=repr(data)[:40]):
                self.assertEqual(self.post(data)[0], 400)

    def test_bad_json(self):
        headers = {"Content-Type": "application/json", "Origin": f"http://127.0.0.1:{self.port}"}
        self.assertEqual(self.request("POST", "/api/chat", "{", headers)[0], 400)
        self.assertEqual(self.request("POST", "/api/chat", b"\xff", headers)[0], 400)

    def test_origin_and_host(self):
        self.assertEqual(self.post({"message":"hi"}, Origin="http://evil.example")[0], 403)
        self.assertEqual(self.post({"message":"hi"}, Host="evil.example")[0], 403)
        self.assertEqual(self.request(headers={"Host":"evil.example"})[0], 403)
        self.assertEqual(self.request("POST", "/api/chat", "{}", {"Content-Type":"application/json"})[0], 403)

    def test_content_type_and_size(self):
        self.assertEqual(self.post({"message":"hi"}, **{"Content-Type":"text/plain"})[0], 415)
        self.assertEqual(self.post({"message":"x"*13000})[0], 413)
        self.assertEqual(self.post({}, **{"Content-Length":"-1"})[0], 413)
        self.assertEqual(self.post({}, **{"Content-Length":"bad"})[0], 400)
        self.assertEqual(self.post({}, **{"Transfer-Encoding":"chunked"})[0], 400)

    def test_paths(self):
        for path in ["/chatbot.py", "/../app.py", "/README.md"]:
            self.assertEqual(self.request(path=path)[0], 404)
        headers = {"Content-Type":"application/json", "Origin": f"http://127.0.0.1:{self.port}"}
        self.assertEqual(self.request("POST", "/missing", "{}", headers)[0], 404)

if __name__ == "__main__":
    unittest.main()
