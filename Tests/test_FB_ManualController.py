"""
Tests for FB_ManualController
"""
import sys
import unittest

# pylint: disable=missing-function-docstring, missing-class-docstring, invalid-name
from os import device_encoding

from connection import cold_reset, conn, wait_cycles, wait_value

COLD_RESET = True


class Tests(unittest.TestCase):

    PREFIX_DEVICE = "PRG_TEST_FB_MANUALCONTROLLER.FbDevValve"
    PREFIX_CONTROLLER = "PRG_TEST_FB_MANUALCONTROLLER.fbManualController"

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

    def test_01_device_added(self) -> None:
        device_name = conn.read_by_name(f"{self.PREFIX_DEVICE}.sName")
        # NOTE: device will be added at index 1, as index 0 is reserved for a dummy device ("No device")
        device_in_array = conn.read_by_name(
            f"{self.PREFIX_CONTROLLER}.arDeviceArray[1].sName"
        )
        self.assertEqual(device_name, device_in_array)

    def test_02_enable_manual(self) -> None:
        conn.write_by_name(f"{self.PREFIX_CONTROLLER}.stHMI.nSelectedDevice", 1)
        conn.write_by_name(f"{self.PREFIX_CONTROLLER}.stHMI.bEnabled", True)
        self.assertTrue(wait_value(f"{self.PREFIX_DEVICE}.bManual", True, 1))

    def test_03_disable_manual(self) -> None:
        conn.write_by_name(f"{self.PREFIX_CONTROLLER}.stHMI.nSelectedDevice", 1)
        conn.write_by_name(f"{self.PREFIX_CONTROLLER}.stHMI.bEnabled", True)
        self.assertTrue(wait_value(f"{self.PREFIX_DEVICE}.bManual", True, 1))
        conn.write_by_name(f"{self.PREFIX_CONTROLLER}.stHMI.bEnabled", False)
        self.assertTrue(wait_value(f"{self.PREFIX_DEVICE}.bManual", False, 1))


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
