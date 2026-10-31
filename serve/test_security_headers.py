"""The security headers added to every HTTP response (serve/server.py Handler.send_response): clickjacking,
MIME-sniffing, referrer leakage and a same-origin content policy.

    python -m unittest serve.test_security_headers -v
"""
import unittest
import urllib.request

from serve.frontend import ChatTemplate
from serve.server import ByteTokenizer, MockEngine, Service, serve


class SecurityHeaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tok = ByteTokenizer()
        cls.svc = Service(MockEngine(tok, "ok", max_context=4096), tok,
                          ChatTemplate("serve/chat_template.jinja"))
        cls.httpd = serve(cls.svc, port=0)
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def get(self, path):
        with urllib.request.urlopen(self.base + path, timeout=10) as r:
            return r.headers

    def test_x_frame_options_sameorigin(self):
        self.assertEqual(self.get("/health")["X-Frame-Options"], "SAMEORIGIN")

    def test_x_content_type_options_nosniff(self):
        self.assertEqual(self.get("/health")["X-Content-Type-Options"], "nosniff")

    def test_referrer_policy_no_referrer(self):
        self.assertEqual(self.get("/health")["Referrer-Policy"], "no-referrer")

    def test_content_security_policy_present(self):
        self.assertEqual(self.get("/health")["Content-Security-Policy"],
                         "default-src 'self'; frame-ancestors 'self'")

    def test_headers_on_every_answer(self):
        for path in ("/health", "/status", "/v1/models", "/"):
            with self.subTest(path=path):
                h = self.get(path)
                self.assertEqual(h["X-Frame-Options"], "SAMEORIGIN", path)
                self.assertEqual(h["X-Content-Type-Options"], "nosniff", path)
                self.assertEqual(h["Referrer-Policy"], "no-referrer", path)
                self.assertIn("Content-Security-Policy", h, path)


if __name__ == "__main__":
    unittest.main()