import unittest

class DataFetcher(unittest.TestCase):
    def setUp(self):
        import src.data_fetcher
        self.data_fetcher = src.data_fetcher
        import build_config
        self.config = build_config

    def test_get_source(self):
        self.assertEqual(self.data_fetcher.get_source(self.config.ROOT_SERVER, "fizz")["url"], "https://fract-mirror.fast-blast.uk")

    def test_get_pkgdata(self):
        correct = {
			"path":"files/ezcmd/ezcmd-1.0.deb",
			"sha256":"76922b2209e762134556c60cccd438f437d70fbf77c6b7bbf543539540b8295e",
			"filename":"ezcmd-1.0.deb"
		}

        self.assertEqual(self.data_fetcher.get_pkgdata("https://fract-mirror.fast-blast.uk", "ezcmd"), correct)

class Downloader(unittest.TestCase):
    def setUp(self):
        import src.downloader 
        self.downloader = src.downloader

if __name__ == '__main__':
    unittest.main()
