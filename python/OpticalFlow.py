import matplotlib.pyplot as plt
import matplotlib.animation as animation
from cv2 import cv2
import array
import sys
import numpy as np
import math
import time

# pip install matplotlib
# pip install opencv-python

try:
    import sim
except:
    print ('--------------------------------------------------------------')
    print ('"sim.py" could not be imported. This means very probably that')
    print ('either "sim.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "sim.py"')
    print ('--------------------------------------------------------------')
    print ('')

point_selected = False
old_points = np.array([[]])   

# Lucas Kanade parameters
lk_params = dict(winSize = (50,50),
                maxLevel = 2,
                criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

def streamVisionSensor():
    global point_selected, old_points
    # Mouse function
    def select_point(event,x,y, flags, params): 
        global point, point_selected, old_points
        if event == cv2.EVENT_LBUTTONDOWN:
            point = (x,y)
            point_selected = True
            old_points = np.array([[x,y]], dtype = np.float32)

    cv2.namedWindow('frame')

    #point = ()
    #old_points = np.array([[]])    


    errorCode,visionSensorHandle = sim.simxGetObjectHandle(clientID,'Vision_sensor',sim.simx_opmode_oneshot_wait)
    errorCode,resolution,image = sim.simxGetVisionSensorImage(clientID,visionSensorHandle,0,sim.simx_opmode_streaming)
    time.sleep(0.5)


    errorCode,resolution,image = sim.simxGetVisionSensorImage(clientID,visionSensorHandle,0,sim.simx_opmode_buffer)
    sensorImage = np.array(image,dtype=np.uint8)
    sensorImage.resize([resolution[1],resolution[0],3])
    sensorImage = cv2.cvtColor(sensorImage, cv2.COLOR_BGR2GRAY)
    sensorImage = cv2.flip(sensorImage,1)
    old_image = sensorImage.copy()


    while (sim.simxGetConnectionId(clientID)!=-1): 
        cv2.setMouseCallback('frame', select_point)


        errorCode,resolution,image = sim.simxGetVisionSensorImage(clientID,visionSensorHandle,0,sim.simx_opmode_buffer)
        sensorImage = np.array(image,dtype=np.uint8)
        sensorImage.resize([resolution[1],resolution[0],3])
        sensorImage = cv2.cvtColor(sensorImage, cv2.COLOR_BGR2GRAY)
        sensorImage = cv2.flip(sensorImage,1)
        
        
        if point_selected:
            new_points, status, error = cv2.calcOpticalFlowPyrLK(old_image, sensorImage, old_points, None, **lk_params)
            old_image = sensorImage.copy() #current frame becomes previous
            old_points = new_points #current x,y points become previous
            x,y = new_points.ravel()
            cv2.circle(sensorImage, (x,y),8, (0,0,0),-1)
               
            
        displayedImage = cv2.resize(sensorImage, (480,480))
        cv2.imshow('frame',displayedImage)
        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
         
    cv2.destroyAllWindows()    
    print ('End of Simulation')
    point_selected = False


print ('Program started')
sim.simxFinish(-1) # just in case, close all opened connections
clientID=sim.simxStart('127.0.0.1',19997,True,True,5000,5) # Connect to CoppeliaSim
if clientID!=-1:
    print ('Connected to remote API server')

    # Now try to retrieve data in a blocking fashion (i.e. a service call):
    res,objs=sim.simxGetObjects(clientID,sim.sim_handle_all,sim.simx_opmode_blocking)
    if res==sim.simx_return_ok:
        print ('Number of objects in the scene: ',len(objs))
    else:
        print ('Remote API function call returned with error code: ',res)

    time.sleep(0.5)

    point = ()
    old_points = np.array([[]])    
    point_selected = False
    
    streamVisionSensor()
    

    # Before closing the connection to CoppeliaSim, make sure that the last command sent out had time to arrive. You can guarantee this with (for exaplte):
    sim.simxGetPingTime(clientID)

    # Now close the connection to CoppeliaSim:
    sim.simxFinish(clientID)
else:
    print ('Failed connecting to remote API server')
print ('Program ended')



