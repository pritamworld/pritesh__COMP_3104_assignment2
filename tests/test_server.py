import json
import threading
import unittest
import urllib.error
import urllib.request

from app.server import create_server


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(0)  # port 0 = let the OS pick a free port
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get(self, path):
        return urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=5)

    def test_health(self):
        with self.get("/health") as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(json.load(resp), {"status": "ok"})

    def test_root_has_message_and_version(self):
        with self.get("/") as resp:
            body = json.load(resp)
        self.assertIn("message", body)
        self.assertIn("version", body)

    def test_unknown_path_is_404(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.get("/nope")
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
