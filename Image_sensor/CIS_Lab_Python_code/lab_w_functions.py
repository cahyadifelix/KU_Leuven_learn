'''
Test lab functions file

Tested with PyCharm 2021.3.2 (Community Edition), Python 3.9.15 and Conda environement.
Update: Pedro Santos - 01-2023

'''

from pypylon import pylon
import cv2
import CIS_lab_functions as fcis

# #### get camera name
nodefile, cameraname, device_name = fcis.get_camera_name()

# #### start camera
camera = fcis.camera_open(nodefile)

# #### start grabbing
converter = fcis.start_grabbing_cont(camera)



if cameraname != "puA1280":
    # #### converting to opencv bgr format
    converter = fcis.conv_opencv_bgr(converter)
    width_out, heigth_out, darkmean, roi_w, roi_h = fcis.camera_frame_set(cameraname)
    width = roi_w
    heigth = roi_h
else:
    # #### converting to opencv bgr format
    converter = fcis.conv_opencv_bw(converter)
    width_out, heigth_out, darkmean, roi_w, roi_h = fcis.camera_frame_set(cameraname)
    width = width_out
    heigth = heigth_out


while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    imraw = grabResult.Array
    if grabResult.GrabSucceeded():
        # Access the image data
        image = converter.Convert(grabResult)
        img = image.GetArray()
        cv2.namedWindow('title', cv2.WINDOW_NORMAL)
        cv2.imshow('title', img)
        width = grabResult.Width
        height = grabResult.Height # grabResult.Heigth
     
        k = cv2.waitKey(1)
#        print (k)
        if k == 27:  ## k = Excape button.
             fcis.stop_camera_grabbing(camera)
             break
        if k == ord('?'):
            fcis.print_help()

        if k == 115: #'s'
            fcis.save_image(imraw, img, "imraw.raw")
             
        if k == ord('v'):
            fcis.print_verbose(grabResult, img, imraw)
            
        if k == ord('h'):
            fcis.display_histogram(imraw)
            
        if k == ord('n'): # noise measurement
            fcis.measure_noise(camera, width, height, 100, 0, 0)
            
        if k == ord('d'):
            fcis.dark_measurement_and_plot(camera, width, height, 100)
     
        if k == ord('p'): #ptc measurement
            fcis.ptc_measurement(camera, width, height, 100)
    grabResult.Release()
# Releasing the resource    
camera.StopGrabbing()
cv2.destroyAllWindows()
