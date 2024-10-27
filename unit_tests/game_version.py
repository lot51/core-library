import unittest
from lot51_core.lib.game_version import GameVersion


class TestGameVersion(unittest.TestCase):
    def setUp(self):
        self.game_version = GameVersion.parse("1.105.345.1220")

    def test_parse(self):
        self.assertEqual(self.game_version.major, 1)
        self.assertEqual(self.game_version.minor, 105)
        self.assertEqual(self.game_version.patch, 345)
        self.assertEqual(self.game_version.platform, 1220)
        self.assertEqual(self.game_version.os, 12)
        self.assertEqual(self.game_version.unused, 20)

    def test_is_valid(self):
        self.assertTrue(self.game_version.is_valid())

    def test_match_correct_different_minor(self):
        self.assertTrue(self.game_version.match(">=1.104.0"))

    def test_match_correct_same_minor(self):
        self.assertTrue(self.game_version.match(">=1.105.0"))

    def test_match_correct_no_patch(self):
        self.assertTrue(self.game_version.match(">=1.104"))

    def test_match_incorrect(self):
        self.assertFalse(self.game_version.match(">=1.105.385"))

    def test_is_mac(self):
        self.assertTrue(self.game_version.is_mac())

    def test_is_windows(self):
        self.assertFalse(self.game_version.is_windows())

    def test_is_legacy(self):
        self.assertFalse(self.game_version.is_legacy())

    def test_to_tuple(self):
        self.assertTupleEqual(self.game_version.to_tuple(), (1, 105, 345, 1220,))

    def test_to_str(self):
        self.assertEqual(self.game_version.to_str(), "1.105.345.1220")

    def test_to_dict(self):
        self.assertDictEqual(self.game_version.to_dict(),
                             {'major': 1,
                              'minor': 105,
                              'patch': 345,
                              'platform': 1220,
                              'os': 12,
                              'unused': 20
                             })


class TestShortGameVersion(unittest.TestCase):
    def setUp(self):
        self.game_version = GameVersion.parse("1.105")

    def test_parse(self):
        self.assertEqual(self.game_version.major, 1)
        self.assertEqual(self.game_version.minor, 105)
        self.assertEqual(self.game_version.patch, 0)
        self.assertEqual(self.game_version.platform, None)
        self.assertEqual(self.game_version.os, None)
        self.assertEqual(self.game_version.unused, None)

    def test_is_valid(self):
        self.assertTrue(self.game_version.is_valid())

    def test_match_correct_different_minor(self):
        self.assertTrue(self.game_version.match(">=1.104.0"))

    def test_match_correct_same_minor(self):
        self.assertTrue(self.game_version.match(">=1.105.0"))

    def test_match_correct_no_patch(self):
        self.assertTrue(self.game_version.match(">=1.105"))

    def test_match_incorrect(self):
        self.assertFalse(self.game_version.match(">=1.105.385"))

    def test_is_mac(self):
        self.assertTrue(self.game_version.is_mac())

    def test_is_windows(self):
        self.assertFalse(self.game_version.is_windows())

    def test_is_legacy(self):
        self.assertFalse(self.game_version.is_legacy())

    def test_to_tuple(self):
        self.assertTupleEqual(self.game_version.to_tuple(), (1, 105, 345, 1220,))

    def test_to_str(self):
        self.assertEqual(self.game_version.to_str(), "1.105.345.1220")

    def test_to_dict(self):
        self.assertDictEqual(self.game_version.to_dict(),
                             {'major': 1,
                              'minor': 105,
                              'patch': 345,
                              'platform': 1220,
                              'os': 12,
                              'unused': 20
                             })
