import unittest

class Downloader(unittest.TestCase):
    def setUp(self):
        import src.downloader
        self.downloader = src.downloader
        import build_config
        self.config = build_config

    def test_get_source(self):
        self.assertEqual(self.downloader.get_source(self.config.ROOT_SERVER, "fizz")["url"], "https://fract-mirror.fast-blast.uk")

if __name__ == '__main__':
    unittest.main()
