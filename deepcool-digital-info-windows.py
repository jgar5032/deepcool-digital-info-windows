#!/usr/bin/env python3
"""
Deepcool Digital Display Windows port
Based on: https://github.com/Algorithm0/deepcool-digital-info (MIT License)

Displays CPU temperature/usage on Deepcool Digital USB HID displays.

"""

import sys
import time
import argparse

import hid
import psutil
import clr

# --- Load LibreHardwareMonitorLib -------------------------------------------
clr.AddReference('LibreHardwareMonitorLib')
from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType

_computer = Computer()
_computer.IsCpuEnabled = True
_computer.Open()

def _get_cpu_package_temp():
    """Return the CPU package temperature in Celsius, or None if unavailable."""
    for hw in _computer.Hardware:
        if hw.HardwareType == HardwareType.Cpu:
            hw.Update()
            fallback = None
            for sensor in hw.Sensors:
                if sensor.SensorType == SensorType.Temperature and sensor.Value is not None:
                    if "Package" in sensor.Name:
                        return round(sensor.Value)
                    if fallback is None:
                        fallback = sensor.Value
            if fallback is not None:
                return round(fallback)
    return None


CUR_DEVICE = "CUSTOM"
INTERVAL = 1
FLIP_INTERVAL = 8

class DeviceInfo:
    def __init__(self, vendor_id, product_id, simple_mode):
        self.VENDOR_ID = vendor_id
        self.PRODUCT_ID = product_id
        self.SIMPLE_MODE = simple_mode

DEVICES = {
    "CH510":  DeviceInfo(vendor_id=0x34D3, product_id=0x1100, simple_mode=True),
    "AK400":  DeviceInfo(vendor_id=0x3633, product_id=0x0001, simple_mode=False),
    "AK500":  DeviceInfo(vendor_id=0x3633, product_id=0x0003, simple_mode=False),
    "AK500S": DeviceInfo(vendor_id=0x3633, product_id=0x0004, simple_mode=False),
    "AK620":  DeviceInfo(vendor_id=0x3633, product_id=0x0002, simple_mode=False),
    "AG400":  DeviceInfo(vendor_id=0x3633, product_id=0x0008, simple_mode=False),
    "CUSTOM": DeviceInfo(vendor_id=0x0000, product_id=0x0000, simple_mode=False),
}

parser = argparse.ArgumentParser(
    description="Deepcool Digital display driver - Windows port")
parser.add_argument('-d', '--device', default=CUR_DEVICE,
                     help='device name from the built-in DEVICES table')
parser.add_argument('-i', '--interval', type=float, default=INTERVAL,
                     help='sensor polling interval in seconds (default: 1)')
parser.add_argument('--flip-interval', type=float, default=FLIP_INTERVAL,
                    help='display flip interval in both mode (default: 5)')
parser.add_argument('-t', '--test', action='store_true',
                     help='send random values, ignoring sensors')
parser.add_argument('--debug', action='store_true',
                    help='print temperature and CPU usage values before sending')
parser.add_argument('-v', '--vendor', type=lambda x: int(x, 0), default=None,
                     help='override VENDOR_ID, e.g. 0x3633')
parser.add_argument('-p', '--product', type=lambda x: int(x, 0), default=None,
                     help='override PRODUCT_ID, e.g. 0x0002')
parser.add_argument('--mode', choices=['temp', 'usage', 'both'], default='both', 
                     help='Display mode (default: both)')
args = parser.parse_args()

INTERVAL = args.interval
FLIP_INTERVAL = args.flip_interval
CUR_DEVICE = args.device.upper()
TST_MODE = args.test
DISPLAY_MODE = args.mode
DEBUG = args.debug

if CUR_DEVICE not in DEVICES:
    print(f"Unknown device '{CUR_DEVICE}'. Known devices: {', '.join(DEVICES.keys())}")
    sys.exit(1)

if args.vendor is not None:
    DEVICES[CUR_DEVICE].VENDOR_ID = args.vendor
if args.product is not None:
    DEVICES[CUR_DEVICE].PRODUCT_ID = args.product

if TST_MODE:
    from random import randint

def get_bar_value(input_value):
    return (input_value - 1) // 10 + 1

def get_data_complex(value=0, mode='util'):
    base_data = [16] + [0] * 63
    numbers = [int(char) for char in str(value)]
    base_data[2] = get_bar_value(value)

    if mode == 'util':
        base_data[1] = 76
    elif mode == 'start':
        base_data[1] = 170
        return base_data
    elif mode == 'temp':
        base_data[1] = 19

    if len(numbers) == 1:
        base_data[5] = numbers[0]
    elif len(numbers) == 2:
        base_data[4], base_data[5] = numbers
    elif len(numbers) == 3:
        base_data[3], base_data[4], base_data[5] = numbers
    elif len(numbers) == 4:
        base_data[3], base_data[4], base_data[5], base_data[6] = numbers

    if CUR_DEVICE == "AG400":
        temp_first_digit = base_data[4]
        temp_second_digit = base_data[5]
        base_data[5] = base_data[3]
        base_data[3] = temp_first_digit
        base_data[4] = temp_second_digit

    return base_data

def get_data_simple(usage: int = 0, temp_c: int = 0):
    simple_data = bytearray()
    simple_data.extend(map(ord, f"_HLXDATA({usage},{temp_c},0,0,C)"))
    return simple_data

def get_temperature(is_test: bool = False):
    if is_test:
        return randint(45, 95)
    temp = _get_cpu_package_temp()
    return temp if temp is not None else 0

def get_usage(is_test: bool = False):
    if is_test:
        return randint(0, 100)
    return round(psutil.cpu_percent(interval=None))

try:
    hidDevice = hid.device()
    hidDevice.open(DEVICES[CUR_DEVICE].VENDOR_ID, DEVICES[CUR_DEVICE].PRODUCT_ID)
    hidDevice.set_nonblocking(1)

    if not DEVICES[CUR_DEVICE].SIMPLE_MODE:
        hidDevice.write(get_data_complex(mode="start"))

    current_mode = "temp"
    last_flip = time.monotonic()

    while True:
        if DEVICES[CUR_DEVICE].SIMPLE_MODE:
            hidDevice.write(
                get_data_simple(
                    usage=get_usage(TST_MODE),
                    temp_c=get_temperature(TST_MODE)
                )
            )
            time.sleep(INTERVAL)
            continue

        if DISPLAY_MODE == "both":
            now = time.monotonic()
            if now - last_flip >= FLIP_INTERVAL:
                current_mode = "usage" if current_mode == "temp" else "temp"
                last_flip = now
            active_mode = current_mode
        else:
            active_mode = DISPLAY_MODE

        if active_mode == "temp":
            value = get_temperature(TST_MODE)
            packet_mode = "temp"
        else:
            value = get_usage(TST_MODE)
            packet_mode = "util"

        if DEBUG:
            print(f"{active_mode}: {value}")

        hidDevice.write(get_data_complex(value=value, mode=packet_mode))
        time.sleep(INTERVAL)
except IOError as ex:
    print(ex)
    print("Failed to open device. Check VENDOR_ID/PRODUCT_ID, or try running as Administrator.")
except KeyboardInterrupt:
    print("\nScript terminated by user.")
finally:
    if 'hidDevice' in locals():
        hidDevice.close()
    _computer.Close()
