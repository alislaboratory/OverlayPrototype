

# How to run:
## Hardware Hookup (Raspberry Pi 5 Only)
1. Connect Ultrawide camera to port cam0, and observer (normal FOV) camera to cam1.
2. Connect SSD1309 transparent display to I2C pins, 3V3 and GND on Pi.

## Software
- Run the following: ```sudo nano /boot/firmware/config.txt```
    - Then change this line: ```camera_auto_detect=1``` to be this ```camera_auto_detect=0```
    - Paste these 2 lines at the very bottom 
        - ```dtoverlay=ov5647,cam1```
        - ```dtoverlay=imx219,cam0```
- Activate your virtual environment. See below for more info

### Virtual Environments
If on a new install, here is how to create a venv which ensures that the code at (30/09/2025) works.
- Install as much as possible system-wide before using pip in the venv. Start with the following packages:
```sudo apt install -y python3-venv python3-picamera2 python3-opencv python3-numpy```
- Then install the rest of the needed libraries (ATM only luma.oled for the transparent display):
    - Create a virtual environment
    - ```pip install --upgrade luma.oled```