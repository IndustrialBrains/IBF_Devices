"""
Tests for Fb_DevValve
"""
# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
import sys
import unittest
from enum import IntEnum

import pyads

from connection import cold_reset, conn, wait_cycles, wait_value

COLD_RESET = True


class E_ValveResetState(IntEnum):
    Res_Idle = 0
    Res_Closed = 1
    Res_Open = 2


class Tests(unittest.TestCase):

    PREFIX = "PRG_TEST_FB_DEVVALVE"

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
        conn.write_by_name(f"{self.PREFIX}.bEnableTests", True)
        return super().setUp()

    def _init(self):
        conn.write_by_name(f"{self.PREFIX}.bInit", True)

    def test_00_init(self):
        self._init()
        self.assertTrue(wait_value(f"{self.PREFIX}.bInit", False, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))

    def test_CmdOpen(self):
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdOpen", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bCmdOpen", False, 1))
        self.assertTrue(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))

    def test_CmdClose(self):
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdClose", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bCmdClose", False, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))
        self.assertTrue(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))

    def test_CmdHold(self):
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdHold", True)

        # Try to open
        conn.write_by_name(f"{self.PREFIX}.bCmdOpen", True)
        wait_cycles(1)
        self.assertTrue(conn.read_by_name(f"{self.PREFIX}.bCmdOpen"))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))
        conn.write_by_name(f"{self.PREFIX}.bCmdOpen", False)

        # Try to close
        conn.write_by_name(f"{self.PREFIX}.bCmdClose", True)
        wait_cycles(1)
        self.assertTrue(conn.read_by_name(f"{self.PREFIX}.bCmdClose"))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))

        # Release hold, and verify open/close works
        conn.write_by_name(f"{self.PREFIX}.bCmdHold", False)
        conn.write_by_name(f"{self.PREFIX}.bCmdOpen", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.q_Open", True, 1))
        conn.write_by_name(f"{self.PREFIX}.bCmdClose", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.q_Close", True, 1))

    def test_CmdManual(self):
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdManual", True)

        # Open manually
        conn.write_by_name(f"{self.PREFIX}.fbDevValve.stManualCtrl.bCmdOpen", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.q_Open", True, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))
        conn.write_by_name(f"{self.PREFIX}.fbDevValve.stManualCtrl.bCmdOpen", False)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.q_Open", False, 1))

        # Close manually
        conn.write_by_name(f"{self.PREFIX}.fbDevValve.stManualCtrl.bCmdClose", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.q_Close", True, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))
        conn.write_by_name(f"{self.PREFIX}.fbDevValve.stManualCtrl.bCmdClose", False)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.q_Close", False, 1))

        # Try to open and close via regular commands (should be blocked)
        conn.write_by_name(f"{self.PREFIX}.bCmdOpen", True)
        self.assertFalse(wait_value(f"{self.PREFIX}.fbDevValve.bCmdOpen", True, 0.1))
        conn.write_by_name(f"{self.PREFIX}.bCmdOpen", False)

        conn.write_by_name(f"{self.PREFIX}.bCmdClose", True)
        self.assertFalse(wait_value(f"{self.PREFIX}.fbDevValve.bCmdClose", True, 0.1))

    def test_CmdReset_Idle(self):
        conn.write_by_name(
            f"{self.PREFIX}.eResetState", E_ValveResetState.Res_Idle, pyads.PLCTYPE_UINT
        )
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdReset", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bCmdReset", False, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))

    def test_CmdReset_Open(self):
        conn.write_by_name(
            f"{self.PREFIX}.eResetState", E_ValveResetState.Res_Open, pyads.PLCTYPE_UINT
        )
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdReset", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bCmdReset", False, 1))
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.q_Open", True, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))

    def test_CmdReset_Close(self):
        conn.write_by_name(
            f"{self.PREFIX}.eResetState",
            E_ValveResetState.Res_Closed,
            pyads.PLCTYPE_UINT,
        )
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdReset", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bCmdReset", False, 1))
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.q_Close", True, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))

    def test_CmdSafeStop_Idle(self):
        conn.write_by_name(
            f"{self.PREFIX}.eSafeState", E_ValveResetState.Res_Idle, pyads.PLCTYPE_UINT
        )
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdSafeStop", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.bIsSafe", True, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))

    def test_CmdSafeStop_Open(self):
        conn.write_by_name(
            f"{self.PREFIX}.eSafeState", E_ValveResetState.Res_Open, pyads.PLCTYPE_UINT
        )
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdSafeStop", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.bIsSafe", True, 1))
        self.assertTrue(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))

    def test_CmdSafeStop_Close(self):
        conn.write_by_name(
            f"{self.PREFIX}.eSafeState",
            E_ValveResetState.Res_Closed,
            pyads.PLCTYPE_UINT,
        )
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdSafeStop", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevValve.bIsSafe", True, 1))
        self.assertFalse(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Open"))
        self.assertTrue(conn.read_by_name(f"{self.PREFIX}.fbDevValve.q_Close"))

    @unittest.skip("TODO, time consuming test, needs callbacks")
    def test_CmdTeach(self):
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdTeach", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bCmdTeach", False, 1))

    @unittest.skip(
        "TODO, needs investigation, bSafetyOk logic is confusing throughout the library"
    )
    def test_SafetyOk(self):
        self._init()
        conn.write_by_name(f"{self.PREFIX}.fbDevValve.bSafetyOk", False)


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
