import cv2
import numpy as np
import utlis
import time
from firebase import firebase

curveList=[]
avgVal=10
def  getLaneCurve(img,display=2): 

    imgcopy= img.copy()
    imgResult=img.copy()
    ####step 1
    imgcanny = utlis.processimage(img)
    
     ####step 2
    hT,wT,c=img.shape
    points = utlis.valTrackbars()
    imgWarp = utlis.warpImg(imgcanny,points,wT,hT)
    imgWarpPoints = utlis.drawPoints(imgcopy, points)
    
    ####step 3 
    middlepoint,imgHist=utlis.getHistogram(imgWarp,display=True,minper=0.5,region=1)
    curveAveragepoint,imgHist=utlis.getHistogram(imgWarp,display=True,minper=0.7)
    #print(basepoint-midpointt)
    curveRaw=curveAveragepoint-middlepoint

    ####step 4 
    curveList.append(curveRaw)
    if len(curveList)> avgVal:
        curveList.pop(0)
    curve = int(sum(curveList)/len(curveList)) 
   
    if curve > 160:        
        text = "Smooth Left"
    elif curve < 30 or curve > 150 and curve <= 160:
        text = "Smooth Right"
    elif curve >= 30 and curve <= 150:
        text = "Straight"
    

     ####step 5
    if display != 0:
       imgInvWarp = utlis.warpImg(imgWarp, points, wT, hT,inv = True)
       imgInvWarp = cv2.cvtColor(imgInvWarp,cv2.COLOR_GRAY2BGR)
       imgInvWarp[0:hT//3,0:wT] = 0,0,0
       imgLaneColor = np.zeros_like(img)
       imgLaneColor[:] = 0, 255, 0
       imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)
       imgResult = cv2.addWeighted(imgResult,1,imgLaneColor,1,0)

    # left_frame = imgResult[0:420, 0:int(wT / 2)]  # half left frame 
    # right_frame = imgResult[0:420, int(wT / 2):wT]  # half right frame 
    # cv2.imshow("left frame", left_frame) 
    # cv2.imshow("Right frame", right_frame)
    midY = 478
    
    cv2.putText(imgResult, 'Direction: '+ text, (wT//7-80,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (230, 50, 50), 3, cv2.LINE_AA) 
    #cv2.putText(imgResult,str(curve),(wT//2-80,85),cv2.FONT_HERSHEY_COMPLEX,2,(255,0,255),3)
    # cv2.line(imgResult,(wT//2,midY),(wT//2+(curve*3),midY),(255,0,255),5)
    # cv2.line(imgResult, ((wT // 2 + (curve * 3)), midY-25), (wT // 2 + (curve * 3), midY+25), (0, 255, 0), 5)
     # cv2.putText(imgResult, 'FPS '+str(int(fps)), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (230,50,50), 3)

    w1 = 60
    w2 = 500
    if curveAveragepoint<w1:
        cv2.putText(imgResult,'Go Right',(w1-40,midY-10),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
        class action1:
            print('Lane detected')
            app = firebase.FirebaseApplication('https://tast-1-e6cef-default-rtdb.firebaseio.com/')
            result = app.post('Lane', {"action2": "Go right"})
            print(result)
    if 600>curveAveragepoint>w2:
       cv2.putText(imgResult,'Go Left',(w2+20,midY-10),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
       class action1:
           print('Lane detected')
           app = firebase.FirebaseApplication('https://tast-1-e6cef-default-rtdb.firebaseio.com/')
           result = app.post('Lane', {"action2": "Go Left"})
           print(result)

        
    if display == 2:
        imgStacked = utlis.stackImages(0.7,([img,imgWarpPoints,imgWarp],
                                         [imgHist,imgLaneColor,imgResult]))
        cv2.imshow('ImageStack',imgStacked)
    elif display == 1:
       cv2.imshow('Resutlt',imgResult)

   
    ####Normalization 
    curve=curve/100
    if curve>1: curve==1
    if curve>-1: curve==-1

    # cv2.imshow('canny',imgcanny)
    # cv2.imshow('warp',imgWarp)
    # cv2.imshow('warp points',imgWarpPoints)
    # cv2.imshow('Histogram',imgHist)
    return curve

if __name__ == '__main__':
    cap = cv2.VideoCapture('vid4.mp4')
    intialTracbarVals = [197,322,60,480]
    utlis.initializeTrackbars(intialTracbarVals)
    frameCounter = 0
    # prev_frame_time = 0
    # new_frame_time = 0
    while True:

        # new_frame_time = time.time()
        # fps = 1/(new_frame_time-prev_frame_time)
        # prev_frame_time = new_frame_time
    
        frameCounter +=1
        if cap.get(cv2.CAP_PROP_FRAME_COUNT) ==frameCounter:
            cap.set(cv2.CAP_PROP_POS_FRAMES,0)
            frameCounter=0
        _, img = cap.read() # GET THE IMAGE
        img = cv2.resize(img,(640,480)) # RESIZE
        curve=getLaneCurve(img,display=1)
        print(curve)
        #cv2.imshow('vid',img)
        cv2.waitKey(1)
        
       