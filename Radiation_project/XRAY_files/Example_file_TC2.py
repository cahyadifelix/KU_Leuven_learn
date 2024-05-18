#   TC2-CIS PTC routine
#
#   written by: Pedro Santos
#   Date: 29/04/2024
#   Version 1.0

#  Imports and module declarations
from ctypes import*
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import time
import os
import keyboard

# Load TC2 dynamic library for register and data interface
TC2_fnc = cdll.LoadLibrary("./TC2-CIS_Py.dll")

# Name to add to the
newname = "DARK_last_aftermeasur"
#       EXPOSURE TIME = 10.5 ms
exp_lsb = 135
exp_msb = 1
# number of frames to capture
nbr_frames = 20
save_path = "./XRAY_Map_cross/"


def split32bit(num):        # split 64bit in 2 words of 32 bits
    binary = bin(num)[2:].rjust(32, '0')
    return int(binary[:16], 2), int(binary[16:], 2)


def set_exposure_time (reg3_val, reg4_val):
    # Set the exposure and timing settings
    sts = TC2_fnc.send_command(3, reg3_val)  # REG 3 - Row time LSB
    sts = TC2_fnc.send_command(4, reg4_val)  # REG 4 - Row time MSB


def frame_read(rg_begin, rg_end):
    pix_val = []
    for i in range(rg_begin, rg_end):
        a = TC2_fnc.send_command(9, i)
        a = abs(a)
        a1, a2 = split32bit(a)
        if a1 > 60000:
            a1 = 0
        if a2 > 60000:
            a2 = 0
        pix_val.append(a1)
        pix_val.append(a2)
    matrix = np.array(pix_val).reshape(-1, 16)
    return matrix


def save_frame(data2save, savepath, filename_frame):
    np.savetxt(savepath + filename_frame + '.csv', data2save, delimiter=',')
    # save an image
    intdata = (np.rint(data2save)).astype(int)
    im = Image.fromarray(intdata)
    im.save(savepath + filename_frame + ".png")
    return 0


# Initial settings #
status = TC2_fnc.send_command(0, 129)   # REG 0 - Load Matrix->A and Digital CDS
status = TC2_fnc.send_command(5, 0)     # REG 5 - Reset reference value LSB
status = TC2_fnc.send_command(6, 16)    # REG 5 - Reset reference value MSB
status = TC2_fnc.send_command(7, 0)     # REG 7 - Signal reference value LSB
status = TC2_fnc.send_command(8, 16)    # REG 8 - Signal reference value MSB
status = TC2_fnc.send_command(2, 15)    # REG 2 - Enable all needed supplies
status = TC2_fnc.send_command(1, 24)    # REG 1 - Full Frame + Cont Run + RST ROW/COL ('0')
status = TC2_fnc.send_command(10, 19)   # REG 10 - start Val timming + bypass=0
status = TC2_fnc.send_command(35, 16)   # REG 37 - Row number read


# ------------------------------------------------------------------
#               Timing control
# ------------------------------------------------------------------
##  RST
sts = TC2_fnc.send_command(11, 20)          # REG 11 - RST Delay LSB
sts = TC2_fnc.send_command(12, 0)           # REG 12 - RST Delay MID
sts = TC2_fnc.send_command(13, 0)           # REG 13 - RST Delay MSB
sts = TC2_fnc.send_command(14, 186)         # REG 14 - RST Enable LSB
sts = TC2_fnc.send_command(15, exp_lsb-1)   # REG 15 - RST Enable MID
sts = TC2_fnc.send_command(16, exp_msb)     # REG 16 - RST Enable MSB
sts = TC2_fnc.send_command(38, 226)         # REG 11 - RST Delay B LSB
sts = TC2_fnc.send_command(39, exp_lsb-1)   # REG 12 - RST Delay B MID
sts = TC2_fnc.send_command(40, exp_msb)     # REG 13 - RST Delay B MSB
##  SEL
sts = TC2_fnc.send_command(17, 20)     # REG 17 - SEL Delay LSB
sts = TC2_fnc.send_command(18, 0)      # REG 18 - SEL Delay MID
sts = TC2_fnc.send_command(19, 0)      # REG 19 - SEL Delay MSB
sts = TC2_fnc.send_command(20, 156)    # REG 20 - SEL Enable LSB
sts = TC2_fnc.send_command(21, exp_lsb-1)     # REG 21 - SEL Enable MID
sts = TC2_fnc.send_command(22, exp_msb)      # REG 22 - SEL Enable MSB
##  SHS
sts = TC2_fnc.send_command(23, 161)     # REG 23 - SHS Delay LSB
sts = TC2_fnc.send_command(24, exp_lsb-1)      # REG 24 - SHS Delay MID
sts = TC2_fnc.send_command(25, exp_msb)      # REG 25 - SHS Delay MSB
sts = TC2_fnc.send_command(26, 181)    # REG 26 - SHS Enable LSB
sts = TC2_fnc.send_command(27, exp_lsb-1)     # REG 27 - SHS Enable MID
sts = TC2_fnc.send_command(28, exp_msb)      # REG 28 - SHS Enable MSB
##  SHR
sts = TC2_fnc.send_command(29, 218)     # REG 29 - SHR Delay LSB
sts = TC2_fnc.send_command(30, exp_lsb-1)      # REG 30 - SHR Delay MID
sts = TC2_fnc.send_command(31, exp_msb)       # REG 31 - SHR Delay MSB
sts = TC2_fnc.send_command(32, 236)    # REG 32 - SHR Enable LSB
sts = TC2_fnc.send_command(33, exp_lsb-1)     # REG 33 - SHR Enable MID
sts = TC2_fnc.send_command(34, exp_msb)      # REG 34 - SHR Enable MSB

time.sleep(1)

# ------------------------------------------------------------------
#               Frame acquisition
# ------------------------------------------------------------------
imgset = np.zeros((16, 16, nbr_frames))
immean = np.zeros((16, 16))
imvar = np.zeros((16, 16))
mean2mean = []
mean2var = []

isExist = os.path.exists(save_path)
if not isExist:
    # Create a new directory because it does not exist
    os.makedirs(save_path)
# set the exposure time
    set_exposure_time(exp_lsb, exp_msb)
    time.sleep(4)

while True:
    # frame read to be scraped
    scrap = frame_read(128, 256)
    for j in range(nbr_frames):
        print(j)
        imgset[:, :, j] = frame_read(128, 256)
    immean[:, :] = np.mean(imgset, axis=2)
    imvar[:, :] = np.var(imgset, axis=2)
    print("Mean value of mean image", immean[:, :].mean())
    print("Mean value of variance", imvar[:, :].mean())
    mean2mean.append(immean[:, :].mean())
    mean2var.append(imvar[:, :].mean())
    print("--------------------------\n")
    filename_frame = "Frame_mean_" + newname
    save_frame(immean[:, :], save_path, filename_frame)
    filename_frame = "Frame_var_" + newname
    save_frame(imvar[:, :], save_path, filename_frame)
    time.sleep(1)

    try:
        print("To Exit type -> quit - or\n")
        newname = input("Set new Xray settings, type a new name and and Press enter to continue\n")
    except SyntaxError:
        pass
    if newname == "quit":
        print("Program will terminate")
        break

    # In case of a creation of a multiple frame capture loop with key press in between we can use:

    #  !!! To be used inside a for loop  !!!
    # try:
    #     newname = input("Set new Xray settings, type a name and and Press enter to continue")
    # except SyntaxError:
    #     pass
