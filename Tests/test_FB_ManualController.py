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
    PREFIX_CONTROLLER = "GVL_DevManual.fbManualControler"

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

    def test_device_added(self) -> None:
        device_name = conn.read_by_name(f"{self.PREFIX_DEVICE}.sName")
        # Device will be added at index 1, as index 0 is reserved for "No device"
        # TODO: This is HMI dependency (first item in list is used to fill the combobox),
        # remove it from the Devices library
        device_in_array = conn.read_by_name(
            f"{self.PREFIX_CONTROLLER}.arDeviceArray[1].sName"
        )
        self.assertEqual(device_name, device_in_array)

    def test_enable_manual(self) -> None:
        # Select device
        # TODO: nCmdLookupindex should be an actual command, not a direct write to a private var from the HMI
        conn.write_by_name(f"{self.PREFIX_CONTROLLER}.nCmdLookupindex", 1)
        # TODO: bManualActive should be an actual command, not a direct write to a private var from the HMI
        conn.write_by_name(f"{self.PREFIX_CONTROLLER}.bManualActive", True)
        wait_cycles(1)
        self.assertTrue(conn.read_by_name(f"{self.PREFIX_DEVICE}.bManual"))

    def test_disable_manual(self) -> None:
        conn.write_by_name(f"{self.PREFIX_CONTROLLER}.nCmdLookupindex", 1)
        conn.write_by_name(f"{self.PREFIX_CONTROLLER}.bManualActive", True)
        wait_cycles(1)
        self.assertTrue(conn.read_by_name(f"{self.PREFIX_DEVICE}.bManual"))
        conn.write_by_name(f"{self.PREFIX_CONTROLLER}.bManualActive", False)
        wait_cycles(1)
        self.assertFalse(conn.read_by_name(f"{self.PREFIX_DEVICE}.bManual"))


if __name__ == "__main__":
    for _ in range(1):  # increase value to repeat the test
        test = unittest.main(verbosity=2, exit=False, failfast=True)
        if not test.result.wasSuccessful():
            sys.exit(-1)
