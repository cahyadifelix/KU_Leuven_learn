'''
GUI Interface to the Lab CIS 2022-2023

Tested with PyCharm 2021.3.2 (Community Edition), Python 3.9.15 and Conda environment.
Update: Pedro Santos - 01-2023

'''

from pypylon import pylon
import os
import CIS_lab_functions as fcis
import cv2
import PySimpleGUI as sg


sg.theme('Black')

# define the window layout
picture = [[sg.Text('KU Leuven - Image Sensors and Processing - Acquisition tool ', size=(50, 1), justification='center',
                    font='Helvetica 18')],
          [sg.Image(filename='E:\RADMEP_stuff\Semester_2_KU_Leuven\KU_Leuven_learn\Image_sensor\CIS_Lab_Python_code\KU_Leuven.png', key='image')]]

options = [[sg.Text(" ", font='Helvetica 14')],
           [sg.Text(" Capture control and display", font='Helvetica 14')],
           [sg.Button('Initialize Camera', size=(15, 1), font='Helvetica 14')],
           [sg.Text(" Camera Name and serial number is: ", font='Helvetica 10')],
           [sg.Text(' --- None ---', key='-SERIAL-')],
           [sg.Button('Start Capture', size=(15, 1), font='Helvetica 14')],
           [sg.Button('Stop', size=(15, 1), font='Helvetica 14')],
           [sg.Button('Exit', size=(15, 1), font='Helvetica 14')],
           [sg.Text(" ", font='Helvetica 14')],
           [sg.HorizontalSeparator()],
           [sg.Text(" Image info functions", font='Helvetica 14')],
           [sg.Button('Histogram', size=(15, 1), font='Helvetica 14')],
           [sg.Button('Image data info', size=(15, 1), font='Helvetica 14')],
           [sg.Button('Save Image', size=(15, 1), font='Helvetica 14'), sg.InputText("Imraw",
                                                                                    size=(15, 1), font='Helvetica 12')],
           [sg.Text(" ", font='Helvetica 14')],
           [sg.HorizontalSeparator()],
           [sg.Text(" Image processing functions", font='Helvetica 14')],
           [sg.Text(" - Number of frames: ", size=(19, 1), font='Helvetica 12'),
            sg.InputText("100", size=(16, 1), font='Helvetica 12')],
           [sg.Text(" - Pixel Position: ", size=(19, 1), font='Helvetica 12'),
            sg.InputText("0", size=(7, 1), font='Helvetica 12'),
            sg.InputText("0", size=(7, 1), font='Helvetica 12')],
           [sg.Button('Dark', size=(15, 1), font='Helvetica 14')],
           [sg.Button('Noise', size=(15, 1), font='Helvetica 14')],
           [sg.Button('PTC', size=(15, 1), font='Helvetica 14')],
           ]

cwd = os.getcwd()
# print("cwd =", cwd)
frames = [[sg.Frame('Functions and Options', font='Helvetica 12', layout=options, size=(400, 900))]]

# Create layout with two columns using precreated frames
layout = [[sg.Column(frames, element_justification='c'), sg.VSeperator(), sg.Column(picture, element_justification='c')]]

# create the window and show it without the plot
window = sg.Window('Demo Application - OpenCV Integration', layout, resizable=True)

recording = False
initialize_cam = False

while True:
    event, values = window.read(timeout=100)
    filename = cwd + "\\Save_Image\\" + str(values[1])
    nbr_frames = int(values[3])
    Xpos = int(values[4])
    Ypos = int(values[5])
    # print (filename)
    if initialize_cam:
        if camera.IsGrabbing():
            grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            imraw = grabResult.Array
            if grabResult.GrabSucceeded():
                # Access the image data
                image = converter.Convert(grabResult)
                img = image.GetArray()
                width = grabResult.Width
                height = grabResult.Height  # grabResult.Heigth
                # recording = True
            # grabResult.Release()
        else:
            grabResult.Release()
            # recording = False
    if recording:
        img_lres = cv2.resize(img, (1280, 960), interpolation=cv2.INTER_AREA)
        imgbytes = cv2.imencode('.png', img_lres)[1].tobytes()  # ditto
        window['image'].update(data=imgbytes)

    if event == 'Exit' or event == sg.WIN_CLOSED:
        try:
            fcis.close_camera_and_exit(camera)
        except:
            print("A camera was not connected. Exiting Now.")
        break

    elif event == 'Initialize Camera':
        # #### get camera name
        nodefile, cameraname, device_name = fcis.get_camera_name()
        print("This is the nodefile",nodefile)
        # #### start camera
        camera = fcis.camera_open(nodefile)
        # #### start grabbing
        converter = fcis.start_grabbing_cont(camera)
        if cameraname == "puA1280" or cameraname == "puA1280" :
            # #### converting to opencv bgr format
            converter = fcis.conv_opencv_rgb(converter)
            width, height, darkmean, roi_w, roi_h = fcis.camera_frame_set(cameraname)
        else:
            # #### converting to opencv bgr format
            converter = fcis.conv_opencv_bw(converter)
            width, height, darkmean, roi_w, roi_h = fcis.camera_frame_set(cameraname)
        window['-SERIAL-'].update(str(device_name))
        initialize_cam = True


    elif event == 'Start Capture':
        recording = True
        img_lres = cv2.resize(img, (1280, 960), interpolation=cv2.INTER_AREA)
        imgbytes = cv2.imencode('.png', img_lres)[1].tobytes()  # ditto
        window['image'].update(data=imgbytes)

    elif event == 'Stop':
        recording = False
        # img = np.full((480, 640), 255)
        # # this is faster, shorter and needs less includes
        img_lres = cv2.resize(img, (1280, 960), interpolation=cv2.INTER_AREA)
        imgbytes = cv2.imencode('.png', img_lres)[1].tobytes()
        window['image'].update(data=imgbytes)

    elif event == 'Histogram':
        if camera.IsGrabbing():
            fcis.display_histogram(imraw)

    elif event == 'Image data info':
        if camera.IsGrabbing():
            sg.Popup('SizeX: ', grabResult.Width,
                     'SizeY: ', grabResult.Height,
                     'RGB  value of 0,0 pixel: ', img[0, 0],
                     'Gray value of 0,0 pixel: ', imraw[0, 0],
                     'RGB  value of 0,1 pixel: ', img[0, 1],
                     'Gray value of 0,1 pixel: ', imraw[0, 1],
                     'RGB  value of 1,0 pixel: ', img[1, 0],
                     'Gray value of 1,0 pixel: ', imraw[1, 0],
                     'RGB  value of 1,1 pixel: ', img[1, 1],
                     'Gray value of 1,1 pixel: ', imraw[1, 1])

    elif event == 'Save Image':
        if camera.IsGrabbing():
            fcis.save_image(imraw, img, filename)

    elif event == 'Dark':
        if camera.IsGrabbing():
            sg.Popup('Cover the lens and then - Press OK: ')
            fcis.dark_measurement_and_plot(camera, width, height, nbr_frames)

    elif event == 'Noise':
        if camera.IsGrabbing():
            fcis.measure_noise(camera, width, height, nbr_frames, Xpos, Ypos)

    elif event == 'PTC':
        if camera.IsGrabbing():
            sg.Popup('Cover the lens and then - Press OK: ')
            darkmean, darknoise, darkmax, darkmeanmean, darkfpn, darknoisemean, darknoisemax = fcis.dark_measurement(camera,
                                                                                                                width,
                                                                                                                height,
                                                                                                             nbr_frames)
            sg.Popup('Remove the lens cover and then - Press OK: ')
            fcis.ptc_measurement_GUI(camera, width, height, nbr_frames, darkmean, darknoise, darkmax, darkmeanmean,
                                     darkfpn, darknoisemean, darknoisemax)

