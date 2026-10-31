"""SSRF protection for the vision image encoder (serve/server.py): every IP a URL's host resolves to is checked
against private, loopback, link-local and other reserved ranges before anything is fetched, so a page that
rebinds a name to the metadata service (or to another machine on the LAN) cannot make the server fetch for it.

    python -m unittest serve.test_ssrf_protection -v
"""
import socket
import unittest
from unittest import mock

from serve.server import Vision


class BlockedIp(unittest.TestCase):
    """Vision._is_blocked_ip: private, loopback, link-local, reserved and multicast are refused; public is allowed."""

    def test_ipv4_loopback(self):
        for ip in ("127.0.0.1", "127.0.0.2", "127.255.255.255", "127.0.0.0"):
            self.assertTrue(Vision._is_blocked_ip(ip), ip)

    def test_ipv4_private(self):
        for ip in ("10.0.0.1", "10.255.255.255", "172.16.0.1", "172.31.255.255",
                   "192.168.0.1", "192.168.255.255"):
            self.assertTrue(Vision._is_blocked_ip(ip), ip)

    def test_ipv4_link_local(self):
        for ip in ("169.254.0.1", "169.254.169.254", "169.254.255.255"):
            self.assertTrue(Vision._is_blocked_ip(ip), ip)

    def test_ipv4_reserved_and_multicast(self):
        for ip in ("0.0.0.0", "0.255.255.255", "100.64.0.1", "100.127.255.255",
                   "224.0.0.1", "239.255.255.255", "240.0.0.1", "255.255.255.255"):
            self.assertTrue(Vision._is_blocked_ip(ip), ip)

    def test_ipv6_blocked(self):
        for ip in ("::1", "fc00::1", "fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",
                   "fe80::1", "fe80::ffff:ffff:ffff:ffff", "febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff"):
            self.assertTrue(Vision._is_blocked_ip(ip), ip)

    def test_invalid_ip_is_blocked(self):
        for ip in ("not an ip", "", "999.999.999.999", "127.0.0.1.1", "2001:db8::g", "1.2.3.4.5"):
            self.assertTrue(Vision._is_blocked_ip(ip), ip)

    def test_public_ips_are_allowed(self):
        for ip in ("8.8.8.8", "1.1.1.1", "93.184.216.34", "2001:4860:4860::8888",
                   "2606:4700:4700::1111", "104.18.22.10"):
            self.assertFalse(Vision._is_blocked_ip(ip), ip)


class ResolveHost(unittest.TestCase):
    """Vision._resolve_host returns every IP a host points at and validates them all."""

    def test_localhost_resolves_to_blocked(self):
        ips = Vision._resolve_host("localhost")
        self.assertTrue(ips, "localhost resolved to nothing")
        for ip in ips:
            self.assertTrue(Vision._is_blocked_ip(ip), ip)

    def test_ipv4_loopback_host(self):
        ips = Vision._resolve_host("127.0.0.1")
        self.assertEqual(ips, ["127.0.0.1"])
        self.assertTrue(Vision._is_blocked_ip(ips[0]))

    def test_ipv6_loopback_host(self):
        try:
            socket.getaddrinfo("::1", None, proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            self.skipTest("IPv6 is not available")
        ips = Vision._resolve_host("::1")
        self.assertEqual(ips, ["::1"])
        self.assertTrue(Vision._is_blocked_ip(ips[0]))

    def test_mapped_ipv4_is_stripped(self):
        with mock.patch("socket.getaddrinfo", return_value=[(socket.AF_INET6, socket.SOCK_STREAM, 0, "",
                                                            ("::ffff:8.8.8.8", 0))]):
            self.assertEqual(Vision._resolve_host("dns-rebinding.example"), ["8.8.8.8"])

    def test_unresolvable_host_raises(self):
        with mock.patch("socket.getaddrinfo", side_effect=socket.gaierror("no such host")):
            with self.assertRaisesRegex(ValueError, "could not be resolved"):
                Vision._resolve_host("no-such-host.example")

    def test_empty_resolution_raises(self):
        with mock.patch("socket.getaddrinfo", return_value=[]):
            with self.assertRaisesRegex(ValueError, "resolved to no IP addresses"):
                Vision._resolve_host("empty.example")

    def test_dns_rebinding_name_points_at_a_blocked_ip(self):
        """A name that rebinds to the cloud metadata address is refused before anything is fetched."""
        with mock.patch("socket.getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "",
                                                             ("169.254.169.254", 0))]):
            with self.assertRaisesRegex(ValueError, "not allowed"):
                Vision.download("http://rebind.example/x.png")


class Download(unittest.TestCase):
    """Vision.download refuses every blocked destination; public ones are fetched (mocked)."""

    def test_metadata_service_is_blocked(self):
        with mock.patch("socket.getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "",
                                                             ("169.254.169.254", 0))]):
            with self.assertRaisesRegex(ValueError, "not allowed"):
                Vision.download("http://169.254.169.254/latest/meta-data/")

    def test_localhost_url_is_blocked(self):
        with mock.patch("socket.getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "",
                                                             ("127.0.0.1", 0))]):
            with self.assertRaisesRegex(ValueError, "not allowed"):
                Vision.download("http://localhost/secret.png")

    def test_private_lan_url_is_blocked(self):
        for ip in ("10.0.0.5", "192.168.1.1", "172.16.0.1"):
            with self.subTest(ip=ip):
                with mock.patch("socket.getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "",
                                                                     (ip, 0))]):
                    with self.assertRaisesRegex(ValueError, "not allowed"):
                        Vision.download(f"http://{ip}/x.png")

    def test_ipv6_loopback_url_is_blocked(self):
        with mock.patch("socket.getaddrinfo", return_value=[(socket.AF_INET6, socket.SOCK_STREAM, 0, "",
                                                             ("::1", 0))]):
            with self.assertRaisesRegex(ValueError, "not allowed"):
                Vision.download("http://[::1]/x.png")

    def test_a_url_with_no_host_is_blocked(self):
        with self.assertRaisesRegex(ValueError, "has no host"):
            Vision.download("file:///etc/passwd")

    def test_public_url_is_fetched(self):
        body = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
        resp = mock.Mock()
        resp.headers = {"Content-Length": str(len(body))}
        resp.read.return_value = body
        resp.__enter__ = mock.Mock(return_value=resp)
        resp.__exit__ = mock.Mock(return_value=False)
        with mock.patch("socket.getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 0, "",
                                                             ("8.8.8.8", 0))]), \
             mock.patch("urllib.request.urlopen", return_value=resp) as urlopen:
            self.assertEqual(Vision.download("https://8.8.8.8/x.png"), body)
        urlopen.assert_called_once()

    def test_every_resolved_ip_is_checked(self):
        """DNS rebinding to several IPs: one blocked one is enough to refuse the whole host."""
        infos = [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("8.8.8.8", 0)),
                 (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 0))]
        with mock.patch("socket.getaddrinfo", return_value=infos), \
             mock.patch("urllib.request.urlopen") as urlopen:
            with self.assertRaisesRegex(ValueError, "not allowed"):
                Vision.download("https://rebind.example/x.png")
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()