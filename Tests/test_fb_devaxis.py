"""
Tests for Fb_DevAxis
"""
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import sys
import unittest

from connection import cold_reset, conn, wait_cycles, wait_value

COLD_RESET = True


class Tests(unittest.TestCase):

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

    def _init(self):
        conn.write_by_name(f"{self.PREFIX}.bInit", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bInit", False, 2))
        conn.write_by_name(f"{self.PREFIX}.fbDevAxis.IAxisSTOOK", True)

        # The simulated axis retains its state after a cold reset.
        # Therefore, a Reset is triggered after init.
        # NOTE: drive parameter changes are retained after the reset!
        conn.write_by_name(f"{self.PREFIX}.bCmdReset", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bCmdReset", False, 2))

    def _home(self):
        """Homing sequence based on MC_HomingMode.MC_DefaultHoming with a N/O reference sensor"""
        self._init()
        conn.write_by_name(f"{self.PREFIX}.fbDevAxis.IAxisHome", True)
        conn.write_by_name(f"{self.PREFIX}.bCmdHome", True)
        wait_cycles(100)
        conn.write_by_name(f"{self.PREFIX}.fbDevAxis.IAxisHome", False)
        self.assertTrue(wait_value(f"{self.PREFIX}.bCmdHome", False, 2))

    def test_00_init(self):
        self._init()

    def test_01_CmdHome(self):
        self._home()

    def test_CmdHold_during_homing(self):
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdHome", True)
        wait_cycles(100)
        conn.write_by_name(f"{self.PREFIX}.bCmdHold", True)
        wait_cycles(100)
        self.assertEqual(conn.read_by_name(f"{self.PREFIX}.fbDevAxis.fVelocity"), 0)

    def test_CmdHold_during_movement(self):
        self._home()
        conn.write_by_name(f"{self.PREFIX}.bCmdMoveAbs", True)
        wait_cycles(50)
        conn.write_by_name(f"{self.PREFIX}.bCmdHold", True)
        wait_cycles(100)
        self.assertEqual(conn.read_by_name(f"{self.PREFIX}.fbDevAxis.fVelocity"), 0)


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
