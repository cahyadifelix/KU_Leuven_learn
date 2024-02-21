'''
These file compiles all the functions required for the camera acquisition software.
Tested on Basler puA1280 (USB3, windows 64bit , python 3.9)

Software tested with PyCharm 2021.3.2 (Community Edition), Python 3.9.15 and Conda environment.
Created by: Pedro Santos - 01-2023

'''

from pypylon import pylon
import cv2
import sys
#import imageio
import numpy as np
from matplotlib import pyplot as plt


def get_camera_name():
    ''' get_camera_name'''
    tl_factory = pylon.TlFactory.GetInstance()
    devices = tl_factory.EnumerateDevices()
    device_name = []
    for device in devices:
        device_name.append(device.GetFriendlyName())
        print(device.GetFriendlyName())
        print("device_name = ", device_name)

    if "puA1280" in str(device_name):
        nodefile = "E:\RADMEP_stuff\Semester_2_KU_Leuven\KU_Leuven_learn\Image_sensor\CIS_Lab_Python_code\puA1280.pfs"  # Load Pulse BW Camera settings
        cameraname = "puA1280"
        print("puA1280.pfs")
    elif "daA1920-160um" in str(device_name):
        nodefile = "daA1920-160um.pfs"  # Load FHD Dart BW Camera settings
        cameraname = "daA1920"
        print("daA1920-160um.pfs")
    elif "daA3840" in str(device_name):
        nodefile = "daA3840-45um.pfs"  # Load 4K Dart RGB Camera settings
        cameraname = "daA3840"
        print("daA3840-45um.pfs")
    elif "daA1920-30uc" in str(device_name):
        nodefile = "daA1920-30uc.pfs"  # Load 4K Dart RGB Camera settings
        cameraname = "daA1920"
        print("daA1920-30uc.pfs")
    else:
        print(" Not valid camera connected. Program will terminate")
        sys.exit()
    return nodefile, cameraname, device_name


def camera_open(nodefile):
    '''camera_open'''
    # conecting to the first available camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()
    print("Reading pls file and load to camera's node map...")
    pylon.FeaturePersistence.Load(nodefile, camera.GetNodeMap(), True)
    return camera


def start_grabbing_cont(camera):
    '''start_grabbing_cont'''
    # Grabing Continusely (video) with minimal delay
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    converter = pylon.ImageFormatConverter()
    return converter


def conv_opencv_rgb(converter):
    '''conv_opencv_rgb'''
    # converting to opencv bgr format
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    return converter

def conv_opencv_bw(converter):
    '''conv_opencv_bw'''
    # converting to opencv bw format
    converter.OutputPixelFormat = pylon.PixelType_Mono8
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
    return converter

def camera_frame_set(cameraname):
    '''camera_frame_set'''
    width = 0
    heigth = 0
    darkmean = np.zeros((heigth, width))
    roi_w = 1278
    roi_h = 960
    if cameraname == "puA1280":
        width = 1278
        heigth = 960
        darkmean = np.zeros((heigth, width))
    if cameraname == "daA1920":
        width = 1920
        heigth = 1200
        darkmean = np.zeros((heigth, width))
    if cameraname == "daA3840":
        width = 3840
        heigth = 2160
        darkmean = np.zeros((heigth, width))
    return width, heigth, darkmean, roi_w, roi_h


def close_camera_and_exit(camera):
    '''close_camera_and_exit'''
    # grabResult.Release()
    camera.StopGrabbing()
    cv2.destroyAllWindows()
    return 0


def stop_camera_grabbing(camera):
    '''stop_camera_grabbing'''
    camera.Close()
    return 0


def print_help():
    '''print_help'''
    print("Commands:")
    print("  Escape :     stop program")
    print("  s(save):     save image as imag.png")
    print("  v(erbose):   print some data about the acquired image")
    print("  d(ark):      acquire dark average image and display noise statistics")
    print("  h(istogram): display image histogram")
    print("  p(tc):       measure photon transfer curve in image (acquire dark image first)")
    print("  n(oise):     calculate noise in set of 100 images (without dark image acquisition)")
    return 0


def save_image(imraw, img, filename):
    '''save_image'''
    cv2.imwrite(filename + ".png", img)
    imraw.tofile(filename + ".raw")
    return 0


def print_verbose(grabResult, img, imraw):
    '''print_verbose'''
    print("SizeX: ", grabResult.Width)
    print("SizeY: ", grabResult.Height)
    print("RGB  value of 0,0 pixel: ", img[0, 0])
    print("Gray value of 0,0 pixel: ", imraw[0, 0])
    print("RGB  value of 0,1 pixel: ", img[0, 1])
    print("Gray value of 0,1 pixel: ", imraw[0, 1])
    print("RGB  value of 1,0 pixel: ", img[1, 0])
    print("Gray value of 1,0 pixel: ", imraw[1, 0])
    print("RGB  value of 1,1 pixel: ", img[1, 1])
    print("Gray value of 1,1 pixel: ", imraw[1, 1])
    return 0


def display_histogram(imraw):
    '''display_histogram'''
    hist, bin_edges = np.histogram(imraw, bins=4096)
    histmax = hist[0:4095].max()
    print(histmax)
    plt.figure()
    plt.title("Histogram of raw image")
    plt.xlabel("Grayscale value")
    plt.ylabel("# pixels")
    plt.ylim([0, histmax])
    plt.grid(True)
    plt.plot(bin_edges[0:-1], hist)
    plt.show()
    return 0


def measure_noise(camera, width, height, nbrframes, pix_x, pix_y):
    '''measure_noise'''
    #  define pix position to be measured by setting pix_x and pix_y
    imgset = np.zeros((height, width, 100))
    for i in range(nbrframes):  #100 frames default
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        imgset[:, :, i] = grabResult.Array
    #    print(i)
    imgnoise = np.std(imgset, axis=2)
    print("Noise value of pixel [ ", pix_x, " ,", pix_y, "]: ", imgnoise[pix_x, pix_y])
    hist, bin_edges = np.histogram(imgnoise, bins=4096)
    histmax = hist[0:4095].max()
    print(histmax)
    plt.figure()
    plt.title("Histogram of raw image")
    plt.xlabel("RMS noise value [DN rms]")
    plt.ylabel("# pixels")
    plt.ylim([0, histmax])
    plt.grid(True)
    #      plt.yscale("Log")
    plt.plot(bin_edges[0:-1], hist)
    print("mean noise %f", np.mean(imgnoise))
    print("median noise %f", np.median(imgnoise))
    plt.show()
    return 0


def dark_measurement(camera, width, height, nbrframes):
    '''dark_measurement'''
    print("Ready to acquire dark frames for noise measurement \n \n")
    print("Cover the lens and then - Press enter\n")
    cv2.waitKey(0)
    darkset = np.ones((height, width, 100)) * 4096
    for i in range(nbrframes):  #100 frames default
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        darkset[:, :, i] = grabResult.Array
    #    print(i)
    darkmean = np.mean(darkset, axis=2)
    darknoise = np.std(darkset, axis=2)
    darkmax = np.max(darkmean)
    darkmeanmean = np.mean(darkmean)
    darkfpn = np.std(darkmean)
    darknoisemean = np.mean(darknoise)
    darknoisemax = np.max(darknoise)
    return darkmean, darknoise, darkmax, darkmeanmean, darkfpn, darknoisemean, darknoisemax


def dark_measurement_and_plot(camera, width, height, nbrframes):
    '''dark_measurement_and_plot'''
    # print("acquiring dark frames for noise measurement")
    # #  input("Ready to capture dark frame? Press enter")
    # darkset = np.ones((height, width, 100)) * 4096
    # for i in range(nbrframes):  #100 frames default
    #     grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    #     darkset[:, :, i] = grabResult.Array
    # #    print(i)
    # darkmean = np.mean(darkset, axis=2)
    # darknoise = np.std(darkset, axis=2)
    # darkmax = np.max(darkmean)
    # darkmeanmean = np.mean(darkmean)
    # darkfpn = np.std(darkmean)
    # darknoisemean = np.mean(darknoise)
    # darknoisemax = np.max(darknoise)
    darkmean, darknoise, darkmax, darkmeanmean, darkfpn, darknoisemean, darknoisemax = dark_measurement(camera, width,
                                                                                                        height, nbrframes)

    plt.figure()
    plt.title("Dark mean image, equalized to 3x mean")
    plt.imshow(darkmean, cmap='gray', vmin=0, vmax=3 * darkmeanmean)
    text = "min %f,  mean: %f, max : %f" % (np.min(darkmean), darkmeanmean, darkmax)
    plt.text(10, -100, text, color='black')
    plt.show(block=False)

    plt.figure()
    plt.title("Dark noise image, equalized to 3x mean")
    plt.imshow(darknoise, cmap='gray', vmin=0, vmax=darknoisemean * 3)
    text = "min %f,  mean: %f, max : %f" % (np.min(darknoise), darknoisemean, darknoisemax)
    plt.text(10, -100, text, color='black')
    plt.show(block=False)

    plt.figure()
    hist, bin_edges = np.histogram(darkmean, bins=4096)
    histmax = hist[0:4095].max()
    plt.title("Histogram of dark average image")
    plt.xlabel("Pixel mean value [DN]")
    plt.ylabel("# pixels [LOG]")
    plt.ylim([0.1, histmax])
    plt.xlim([0, darkmax])
    plt.grid(True)
    plt.yscale("Log")
    plt.plot(bin_edges[0:-1], hist)
    print("mean level of dark mean image: ", np.mean(darkmean))
    print("median level of dark mean image: ", np.median(darkmean))
    print("standard deviation of mean of dark images: ", darkfpn)
    print("max value of mean of dark images: ", darkmax)
    text = "min %3f,  mean: %3f, max : %3f, median: %3f" % (np.min(darkmean), np.mean(darkmean), darkmax,
                                                            np.median(darkmean))
    plt.text(10, histmax * 0.6, text, color='blue')
    plt.show(block=False)

    plt.figure()
    darknoisesub = darknoise[::2, ::2]
    hist, bin_edges = np.histogram(darknoisesub, bins=4096)
    histmax = hist[0:4095].max()
    plt.title("Histogram of dark noise image")  # 1 color channel
    plt.xlabel("Pixel noise value [DN rms]")
    plt.ylabel("# pixels (log scale)")
    plt.ylim([0.1, histmax])
    plt.xlim([0, darknoisemax])
    plt.grid(True)
    plt.yscale("Log")
    plt.plot(bin_edges[0:-1], hist)
    print("mean value of dark temporal noise image", np.mean(darknoise))
    print("median value of dark temporal noise image", np.median(darknoise))
    print("standard deviation value of dark temporal noise image", np.std(darknoise))
    print("max value of pixel standard deviation over all captured frames: ", darknoisemax)
    text = "min %3f,  mean: %3f, max : %3f, median: %3f" % (
    np.min(darknoise), np.mean(darknoise), darknoisemax, np.median(darknoise))
    plt.text(10, histmax * 0.6, text, color='blue')
    plt.show()
    return 0


def ptc_measurement(camera, width, height, nbrframes):
    '''ptc_measurement'''
    print("starting PTC measurement. Be sure to acquire dark frame first")
    # print("Cover the lens and then - Press enter\n")
    # cv2.waitKey(0)
    darkmean, darknoise, darkmax, darkmeanmean, darkfpn, darknoisemean, darknoisemax = dark_measurement(camera, width,
                                                                                                        height,
                                                                                                        nbrframes)
    print("Remove cover from the lens and then - Press enter\n")
    cv2.waitKey(0)
    imgset = np.ones((height, width, 100)) * 4096
    for i in range(nbrframes):  #100 frames default
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        imgset[:, :, i] = grabResult.Array
    #    print(i)
    immean = np.mean(imgset, axis=2) - darkmean
    #            immean=np.mean(imgset,axis=2)
    imvar = np.var(imgset, axis=2)
    print("Max value of mean image", immean.max())
    print("Max value of variance", imvar.max())
    print("Mean value of mean image", immean.mean())
    print("Mean value of variance", imvar.mean())

    y1 = imvar.flatten()
    x1 = immean.flatten()
    #           z = np.polyfit(imvar[400:500:2,500:600:2].flatten(),immean[400:500:2,500:600:2].flatten(),1)
    z = np.polyfit(x1, y1, 1)
    print("linear fit: ax + b with a,b = ", z)
    p = np.poly1d(z)
    x = ([0, 1, 4095])
    y = p(x)
    #            print(y)
    x2 = x1[:, np.newaxis]
    #  w = np.linalg.lstsq(imvar[400:500:2,500:600:2].flatten(),immean[400:500:2,500:600:2].flatten())
    w, _, _, _ = np.linalg.lstsq(x2, y1, rcond=None)
    print("linear fit: ax with a = ", w[0])

    plt.figure()
    plt.title("PTC curve")
    plt.xlabel("Mean value [DN]")
    plt.ylabel("Variance [DN2]")
    plt.grid(True)
    plt.plot(immean, imvar, '.b')
    plt.plot(x, y, 'r')
    plt.plot(x, w * x, 'm')
    plt.ylim([0, (p([4096]) * 1.25)])
    ypos = (plt.gca().get_ylim())[1]
    text = "linear fit y = %3f x+%3f" % (z[0], z[1])
    plt.text(10, ypos * 0.9, text, fontsize=12, color='r')
    text = "linear fit: y = %3f x" % w[0]
    plt.text(10, ypos * 0.8, text, fontsize=12, color='m')
    plt.show(block=False)

    plt.figure()
    plt.title("PTC curve - log scale")
    plt.xlabel("Mean value [DN]")
    plt.ylabel("Variance [DN2]")
    plt.grid(True)
    plt.ylim([1, (p([4096]) * 2)])
    plt.yscale('log')
    plt.xscale('log')
    plt.plot(immean, imvar, '.b')
    #            plt.plot(x,y,'r')
    plt.plot(x, w * x, 'm')
    ypos = (plt.gca().get_ylim())[1]
    xpos = (plt.gca().get_xlim())[0]
    #            text = "linear fit y = %3f x+%3f" % (z[0],z[1])
    #            plt.text(10, ypos*0.9, text, fontsize = 12, color = 'r')
    text = "linear fit: y = %3f x" % w[0]
    plt.text(xpos * 2, 6, text, fontsize=12, color='m')
    plt.show(block=False)

    y1r = imvar[400:500:2, 500:600:2].flatten()
    x1r = immean[400:500:2, 500:600:2].flatten()
    #           zr = np.polyfit(imvar[400:500:2,500:600:2].flatten(),immean[400:500:2,500:600:2].flatten(),1)
    zr = np.polyfit(x1r, y1r, 1)
    print("linear fit in ROI: ax + b with a,b = ", zr)
    pr = np.poly1d(zr)
    xr = ([0, 4095])
    yr = pr(xr)
    #            print(yr)
    x2r = x1r[:, np.newaxis]
    #            w = np.linalg.lstsq(imvar[400:500:2,500:600:2].flatten(),immean[400:500:2,500:600:2].flatten())
    wr, _, _, _ = np.linalg.lstsq(x2r, y1r, rcond=None)
    print("linear fit in ROI: ax with a = ", wr[0])

    plt.figure()
    plt.title("PTC curve - center ROI")
    plt.xlabel("Mean value [DN]")
    plt.ylabel("Variance [DN2]")
    plt.grid(True)
    plt.ylim([0, (pr([4096]) * 1.25)])
    plt.plot(immean[400:500:2, 500:600:2], imvar[400:500:2, 500:600:2], '.b')
    plt.plot(xr, yr, 'r')
    plt.plot(xr, wr * xr, 'm')
    text = "linear fit y = %3f x+%3f" % (zr[0], zr[1])
    ypos = (plt.gca().get_ylim())[1]
    plt.text(10, ypos * 0.9, text, fontsize=12, color='r')
    text = "linear fit: y = %3f x" % wr[0]
    plt.text(10, ypos * 0.8, text, fontsize=12, color='m')
    plt.show(block=False)

    plt.figure()
    plt.title("PTC curve - center ROI - LOG")
    plt.xlabel("Mean value [DN]")
    plt.ylabel("Variance [DN2]")
    plt.grid(True)
    plt.ylim([1, (pr([4096]) * 2)])
    plt.yscale('log')
    plt.xscale('log')
    plt.plot(immean[400:500:2, 500:600:2], imvar[400:500:2, 500:600:2], '.b')
    #            plt.plot(xr,yr,'r')
    plt.plot(xr, wr * xr, 'm')
    ypos = (plt.gca().get_ylim())[1]
    xpos = (plt.gca().get_xlim())[0]
    #            text = "linear fit y = %3f x+%3f"  % (zr[0],zr[1])
    #            plt.text(10, ypos*0.9, text, fontsize = 12, color = 'r')
    text = "linear fit: y = %3f x" % wr[0]
    plt.text(xpos * 2, 6, text, fontsize=12, color='m')
    plt.show(block=False)

    plt.figure()
    plt.imshow(immean, cmap='gray', vmin=0, vmax=4095)
    plt.show(block=False)

    plt.figure()
    prl = (pr([4095]) * 2)[0]
    plt.hist2d(x1, y1, bins=(256, 256), range=([0, 4095], [0, prl]), cmap=plt.cm.jet)
    plt.colorbar()
    plt.show()


def ptc_measurement_GUI(camera, width, height, nbrframes, darkmean, darknoise, darkmax, darkmeanmean, darkfpn, darknoisemean, darknoisemax):
    '''ptc_measurement for the GUI'''
    # print("starting PTC measurement. Be sure to acquire dark frame first")
    # # print("Cover the lens and then - Press enter\n")
    # # cv2.waitKey(0)
    # darkmean, darknoise, darkmax, darkmeanmean, darkfpn, darknoisemean, darknoisemax = dark_measurement(camera, width,
    #                                                                                                     height,
    #                                                                                                     nbrframes)
    print("Remove cover from the lens and then - Press enter\n")
    cv2.waitKey(0)
    imgset = np.ones((height, width, 100)) * 4096
    for i in range(nbrframes):  #100 frames default
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        imgset[:, :, i] = grabResult.Array
    #    print(i)
    immean = np.mean(imgset, axis=2) - darkmean
    #            immean=np.mean(imgset,axis=2)
    imvar = np.var(imgset, axis=2)
    print("Max value of mean image", immean.max())
    print("Max value of variance", imvar.max())
    print("Mean value of mean image", immean.mean())
    print("Mean value of variance", imvar.mean())

    y1 = imvar.flatten()
    x1 = immean.flatten()
    #           z = np.polyfit(imvar[400:500:2,500:600:2].flatten(),immean[400:500:2,500:600:2].flatten(),1)
    z = np.polyfit(x1, y1, 1)
    print("linear fit: ax + b with a,b = ", z)
    p = np.poly1d(z)
    x = ([0, 1, 4095])
    y = p(x)
    #            print(y)
    x2 = x1[:, np.newaxis]
    #  w = np.linalg.lstsq(imvar[400:500:2,500:600:2].flatten(),immean[400:500:2,500:600:2].flatten())
    w, _, _, _ = np.linalg.lstsq(x2, y1, rcond=None)
    print("linear fit: ax with a = ", w[0])

    plt.figure()
    plt.title("PTC curve")
    plt.xlabel("Mean value [DN]")
    plt.ylabel("Variance [DN2]")
    plt.grid(True)
    plt.plot(immean, imvar, '.b')
    plt.plot(x, y, 'r')
    plt.plot(x, w * x, 'm')
    plt.ylim([0, (p([4096]) * 1.25)])
    ypos = (plt.gca().get_ylim())[1]
    text = "linear fit y = %3f x+%3f" % (z[0], z[1])
    plt.text(10, ypos * 0.9, text, fontsize=12, color='r')
    text = "linear fit: y = %3f x" % w[0]
    plt.text(10, ypos * 0.8, text, fontsize=12, color='m')
    plt.show(block=False)

    plt.figure()
    plt.title("PTC curve - log scale")
    plt.xlabel("Mean value [DN]")
    plt.ylabel("Variance [DN2]")
    plt.grid(True)
    plt.ylim([1, (p([4096]) * 2)])
    plt.yscale('log')
    plt.xscale('log')
    plt.plot(immean, imvar, '.b')
    #            plt.plot(x,y,'r')
    plt.plot(x, w * x, 'm')
    ypos = (plt.gca().get_ylim())[1]
    xpos = (plt.gca().get_xlim())[0]
    #            text = "linear fit y = %3f x+%3f" % (z[0],z[1])
    #            plt.text(10, ypos*0.9, text, fontsize = 12, color = 'r')
    text = "linear fit: y = %3f x" % w[0]
    plt.text(xpos * 2, 6, text, fontsize=12, color='m')
    plt.show(block=False)

    y1r = imvar[400:500:2, 500:600:2].flatten()
    x1r = immean[400:500:2, 500:600:2].flatten()
    #           zr = np.polyfit(imvar[400:500:2,500:600:2].flatten(),immean[400:500:2,500:600:2].flatten(),1)
    zr = np.polyfit(x1r, y1r, 1)
    print("linear fit in ROI: ax + b with a,b = ", zr)
    pr = np.poly1d(zr)
    xr = ([0, 4095])
    yr = pr(xr)
    #            print(yr)
    x2r = x1r[:, np.newaxis]
    #            w = np.linalg.lstsq(imvar[400:500:2,500:600:2].flatten(),immean[400:500:2,500:600:2].flatten())
    wr, _, _, _ = np.linalg.lstsq(x2r, y1r, rcond=None)
    print("linear fit in ROI: ax with a = ", wr[0])

    plt.figure()
    plt.title("PTC curve - center ROI")
    plt.xlabel("Mean value [DN]")
    plt.ylabel("Variance [DN2]")
    plt.grid(True)
    plt.ylim([0, (pr([4096]) * 1.25)])
    plt.plot(immean[400:500:2, 500:600:2], imvar[400:500:2, 500:600:2], '.b')
    plt.plot(xr, yr, 'r')
    plt.plot(xr, wr * xr, 'm')
    text = "linear fit y = %3f x+%3f" % (zr[0], zr[1])
    ypos = (plt.gca().get_ylim())[1]
    plt.text(10, ypos * 0.9, text, fontsize=12, color='r')
    text = "linear fit: y = %3f x" % wr[0]
    plt.text(10, ypos * 0.8, text, fontsize=12, color='m')
    plt.show(block=False)

    plt.figure()
    plt.title("PTC curve - center ROI - LOG")
    plt.xlabel("Mean value [DN]")
    plt.ylabel("Variance [DN2]")
    plt.grid(True)
    plt.ylim([1, (pr([4096]) * 2)])
    plt.yscale('log')
    plt.xscale('log')
    plt.plot(immean[400:500:2, 500:600:2], imvar[400:500:2, 500:600:2], '.b')
    #            plt.plot(xr,yr,'r')
    plt.plot(xr, wr * xr, 'm')
    ypos = (plt.gca().get_ylim())[1]
    xpos = (plt.gca().get_xlim())[0]
    #            text = "linear fit y = %3f x+%3f"  % (zr[0],zr[1])
    #            plt.text(10, ypos*0.9, text, fontsize = 12, color = 'r')
    text = "linear fit: y = %3f x" % wr[0]
    plt.text(xpos * 2, 6, text, fontsize=12, color='m')
    plt.show(block=False)

    plt.figure()
    plt.imshow(immean, cmap='gray', vmin=0, vmax=4095)
    plt.show(block=False)

    plt.figure()
    prl = (pr([4095]) * 2)[0]
    plt.hist2d(x1, y1, bins=(256, 256), range=([0, 4095], [0, prl]), cmap=plt.cm.jet)
    plt.colorbar()
    plt.show()
