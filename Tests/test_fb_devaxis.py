"""Tests for Fb_DevAxis"""
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import sys
import unittest

from connection import cold_reset, conn, wait_cycles

COLD_RESET = True


class TestFb_DevAxis(unittest.TestCase):

    PREFIX = "PRG_TEST_FB_DEVAXIS"

    @classmethod
    def setUpClass(cls) -> None:
        conn.open()
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        conn.close()

    def setUp(self) -> None:
        if COLD_RESET:
            cold_reset()
        return super().setUp()

    @staticmethod
    def _trigger_falling_edge(var: str) -> None:
        conn.write_by_name(var, True)
        wait_cycles(1)
        conn.write_by_name(var, False)
        wait_cycles(1)

    @staticmethod
    def _trigger_rising_edge(var: str) -> None:
        conn.write_by_name(var, False)
        wait_cycles(1)
        conn.write_by_name(var, True)
        wait_cycles(1)

    def test_00_init(self):
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.bInitBusy"))


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
