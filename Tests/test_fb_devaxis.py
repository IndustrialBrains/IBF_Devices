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
    AXIS_STATUS = f"{PREFIX}.fbDevAxis.AxisRef.Status"
    VALID_POS_SETPOINT = 500
    INVALID_POS_SETPOINT = 10000  # outside software limit switch

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

    def _assert_moving(self, status):
        if status:
            self.assertTrue(wait_value(f"{self.AXIS_STATUS}.Moving", True, 2))
        else:
            self.assertTrue(wait_value(f"{self.AXIS_STATUS}.NotMoving", True, 2))

    def _assert_error(self, status):
        self.assertTrue(conn.read_by_name(f"{self.PREFIX}.fbDevAxis.bError") == status)

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
        self._assert_moving(True)
        conn.write_by_name(f"{self.PREFIX}.fbDevAxis.IAxisHome", False)
        self.assertTrue(wait_value(f"{self.PREFIX}.bCmdHome", False, 2))

    def test_00_init(self):
        self._init()

    def test_01_CmdHome(self):
        self._home()

    def test_CmdHold_during_homing(self):
        self._init()
        conn.write_by_name(f"{self.PREFIX}.bCmdHome", True)
        self._assert_moving(True)
        conn.write_by_name(f"{self.PREFIX}.bCmdHold", True)
        self._assert_moving(False)
        self._assert_error(True)

    def test_CmdHold_during_movement(self):
        self._home()
        conn.write_by_name(f"{self.PREFIX}.bCmdMoveAbs", True)
        self._assert_moving(True)
        conn.write_by_name(f"{self.PREFIX}.bCmdHold", True)
        self._assert_moving(False)
        self._assert_error(False)

    def test_CmdHalt_during_movement(self):
        self._home()
        conn.write_by_name(f"{self.PREFIX}.bCmdMoveAbs", True)
        self._assert_moving(True)
        conn.write_by_name(f"{self.PREFIX}.bCmdHalt", True)
        self._assert_moving(False)
        self._assert_error(False)

    def test_CmdMoveAbs(self):
        self._home()
        conn.write_by_name(f"{self.PREFIX}.fPosition", self.VALID_POS_SETPOINT)
        conn.write_by_name(f"{self.PREFIX}.bCmdMoveAbs", True)
        self._assert_moving(True)

    def test_CmdMoveAbs_invalid_setpoint(self):
        self._home()
        conn.write_by_name(f"{self.PREFIX}.fPosition", self.INVALID_POS_SETPOINT)
        conn.write_by_name(f"{self.PREFIX}.bCmdMoveAbs", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevAxis.bError", True, 1))

    def test_CmdReset(self):
        # trigger an error by calling CmdMoveAbs with an invalid setpoint

        # TODO: remove
        conn.write_by_name(f"{self.PREFIX}.fVelocity", 0.01)

        self._home()
        conn.write_by_name(f"{self.PREFIX}.fPosition", self.INVALID_POS_SETPOINT)
        conn.write_by_name(f"{self.PREFIX}.bCmdMoveAbs", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.fbDevAxis.bError", True, 1))

        # axis should not continue moving until reset is triggered
        conn.write_by_name(f"{self.PREFIX}.fPosition", self.VALID_POS_SETPOINT)
        self._assert_moving(False)

        # now reset; motion will resume immediately (MoveAbs command is still in the buffer))
        conn.write_by_name(f"{self.PREFIX}.bCmdReset", True)
        self.assertTrue(wait_value(f"{self.PREFIX}.bCmdReset", False, 1))
        self._assert_moving(True)


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
