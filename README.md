# deepcool-digital-info-windows
Windows port of the Linux DeepCool Digital USB display driver for certain CPU coolers with digital displays.

--

<img width="300" height="300" alt="cooler" src="https://github.com/user-attachments/assets/3256f929-306b-43af-8cd9-ea5c5462e65f" />

--

I decided to make this because DeepCool's standard windows software uses up more system resources than I would like, and I feel better knowing exactly what this software is doing as opposed to DeepCool's close-source version.

This is based on Algorithm0's deepcool-digital-info project for Linux

## Current Features

- Display CPU temp or CPU utilization %
- switch between temp, utilization, or alternating modes
- Works with some DeepCool USB HID displays (compatibility list below)
- Automatic startup via Task Scheduler

## Requirements
- Python 3.11+
- hid
- psutil
- pythonnet
- LibreHardwareMonitorLib.dll (Get it from [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases))
- System.Memory.dll (Get it from [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases))
- System.Runtime.CompilerServices.Unsafe.dll (Get it from [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases))
- PawnIO

## Setup:
1. Make sure you have python installed
2. pip install hid psutil pythonnet
3. download LibreHardwareMonitor - I used release v0.9.6 - if you run the LibreHardwareMonitor .exe, you'll be prompted to download PawnIO, which you will need. 
4. grab LibreHardwareMonitorLib.dll, System.Memory.dll, and System.Runtime.CompilerServices.Unsafe.dll from the ZIP file and place them in a directory alongside deepcool-digital-info-windows.py.

**Getting it set up to run in the background at start up** - a few of these are just my personal preference, so use your own judgement.

1. Open Task Scheduler and click Create Task (not Create Basic Task)
2. General Tab: Name it something like "DeepCool Digital Display", Run whether user is logged on or not, check "Run with Highest Privileges", Configure for Win 10/11
3. Triggers Tab: "New", Begin the task "at startup"
4. Actions Tab: "New", for 'Program/Script', browse to pythonw.exe, my path is C\Users\[USER]\AppData\Local\Programs\Python\Python314\pythonw.exe, for 'Add arguments', put in your python command, there’s an example below. the script and the 3 files. Mine live in a folder in Program Files. For Start in, select the _directory_ where your files are, mine is a folder within Program files. 
5. Conditions Tab: uncheck every box
6. Settings Tab: I checked the first, second, and fifth boxes. For the last drop-down, I selected "Do not start a new instance". You're done now. 

## Run:
**example command - run with admin privileges**

C:\path\to\file\deepcool-digital-info-windows.py -d ak500s --mode both

this is what I use for my cooler, you should change "ak500s" to whichever cooler you are using. If you want just CPU temp or utilization you can do --mode temp or --mode usage. If your cooler is not supported, you can try it anyway by replacing "-d ak500s" with "-v 0x0123 -p 0x0123", replacing those two values with your USB vendor ID and product ID.

extensive list of arguments:
- -t, --test : Send random values instead of reading sensors.
- -i, --interval : Sensor polling interval in seconds (default: 1).
- -v, --vendor : Override the USB Vendor ID (use along with -p).
- -p, --product : Override the USB Product ID (use along with -v).
- -d, --device xyz : Select a device from the built-in device list.
- --mode xyz : Display mode: temp, usage, or both (default: both).
- --flip-interval : Time in seconds before switching displays in "both" mode (default: 8).
- --debug : Print sensor values to the console.

## Compatibility
Supports:
  - AK400
  - AK500
  - AK500S
  - AK620
  - AG400
  - CH510


## Credits

Big thank you to Algorithm0 for the original linux version! This windows version is very much based off of that. 

Original Linux project:

https://github.com/Algorithm0/deepcool-digital-info
