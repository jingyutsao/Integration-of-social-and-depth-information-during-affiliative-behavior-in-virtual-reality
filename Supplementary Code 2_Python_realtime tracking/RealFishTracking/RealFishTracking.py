import PySpin
import numpy        as np
import pandas       as pd
import sys
import os
import cv2
import time
import curses
import dlclive
from pathlib        import Path

from RealFishTracking.utils.MyLogger    import logger       # logging format handling
from RealFishTracking.utils.ExpConfig   import expCfg       # configuration handling
from RealFishTracking.UdpSocket         import UdpSocket    # handle the socket between unity and python
from RealFishTracking.utils.CamUtils    import *
from RealFishTracking.RealFishTracking  import *

dlcProc = dlclive.Processor()

# Global flag
ncursesDisplay = True

def initializeCurses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    return stdscr


def cleanupCurses(stdscr):
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


def labelTopViewFrame(frame, pose):
    head = [int((pose[0,0] + pose[1,0] + pose[2,0])/3), int((pose[0,1] + pose[1,1] + pose[2,1])/3)]
    body = [int(pose[3,0]), int(pose[3,1])]
    cv2.circle(frame, head, 16, (0, 255, 0), 2)
    cv2.line(frame, head, body, (0, 0, 255), 2)

    


def calcPositionAndHeadingAngle(poseEst):
    topRoi = expCfg.getRegionOfInterestFromCfg()['top']
    topCmToPixelRatio = (9.5/topRoi[2])

    bodyX = (poseEst[10]) * topCmToPixelRatio
    bodyZ = (poseEst[9]) * topCmToPixelRatio
    
    # 0 < abs(theta) < 90 -> facing left, 90 < abs(theta) < 180 -> facing right
    headX = ((poseEst[1]+poseEst[4]+poseEst[7])/3) * topCmToPixelRatio
    headZ = ((poseEst[0]+poseEst[3]+poseEst[6])/3) * topCmToPixelRatio
    headingVector = np.array([headX, headZ]) - np.array([bodyX, bodyZ])
    headingAngle = np.angle(headingVector[0]+headingVector[1]*1j, deg=True)
    return np.array([bodyX, bodyZ, headingAngle])


def acquireAndDisplayImages(cams, dlcLive,dlcLive_2) -> bool:
    maxExpFrameNum = expCfg.getMaximumExperimentFrameNum()
    doSaveVideo = expCfg.doSaveVideo()

    logger.info("About to do the image acquisition...")
    poses = np.zeros([maxExpFrameNum, 15])
    poses_sid = np.zeros([maxExpFrameNum, 15])
    times = np.zeros([maxExpFrameNum, 5])

    logger.debug("Retrieve buffer status node and resulting FPS node.")
    bufferStatusNode, ret = getStreamBufferStatusNodes(cams['sid'])
    if ret is not True: return ret
    resultingFPSNode, ret = getResultingFrameRateNodes(cams['sid'])
    if ret is not True: return ret

    # setup fourcc & outcc if user want to save the video
    if doSaveVideo:
        logger.debug("User choose to save the video, instantiate the output stream.")
        fps = expCfg.getAcqFrameRateFromCfg()
        roi = expCfg.getRegionOfInterestFromCfg()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        topOut = cv2.VideoWriter(expCfg.getProjectNameFromCfg() + "_topView.avi",\
                                 fourcc, fps, (roi['top'][2], roi['top'][3]))
        sidOut = cv2.VideoWriter(expCfg.getProjectNameFromCfg() + "_sideView.avi",\
                                 fourcc, fps, (roi['sid'][2], roi['sid'][3]))
    
    logger.debug("Instantiate the UDP socket.")
    udpSocket = UdpSocket('127.0.0.1', 20486)
    udpSocket_2 = UdpSocket('127.0.0.1', 20487)
    logger.info("Begin acquisition images...")
    if ncursesDisplay is True: stdscr = initializeCurses()
    cams['top'].BeginAcquisition()
    cams['sid'].BeginAcquisition()
    prevCycleStart = time.time()
    try:
        for frameCnt in range(maxExpFrameNum):
            currCycleStart = time.time()
            cycleTime = currCycleStart - prevCycleStart
            prevCycleStart = currCycleStart

            # acquire images from TOP view and estimate the posture
            imageTop = cams['top'].GetNextImage(1000)
            if imageTop.IsIncomplete():
                logger.warning('Image incomplete with image status %d ...' % imageTop.GetImageStatus())
                continue
            imageTop = imageTop.GetNDArray()
            poseEstFromTop = dlcLive.get_pose(imageTop)
            

            # acquire images from SIDE view and estimate the posture
            imageSid = cams['sid'].GetNextImage(1000)
            if imageSid.IsIncomplete():
                logger.warning('Image incomplete with image status %d ...' % imageSid.GetImageStatus())
                continue
            imageSid = imageSid.GetNDArray()
            poseEstFromSid = dlcLive_2.get_pose(imageSid)

            # flatten the array and combine two array together
            poseEst = np.reshape(poseEstFromTop,15)
            msgToSend = calcPositionAndHeadingAngle(poseEst)
            coorToSend = np.array2string(msgToSend, separator=',', suppress_small=True)
            msgToSend = str(frameCnt) + coorToSend + str(time.time_ns())
            udpSocket.sendCoordinate(msgToSend)

            # flatten the array and combine two array together
            poseSid = np.reshape(poseEstFromSid,15)
            msgToSend_2 = calcPositionAndHeadingAngle(poseSid)
            coorToSend = np.array2string(msgToSend_2, separator=',', suppress_small=True)
            msgToSend_2 = str(frameCnt) + coorToSend + str(time.time_ns())
            udpSocket_2.sendCoordinate(msgToSend_2)
            
            
            

            imageTop = cv2.cvtColor(imageTop, cv2.COLOR_GRAY2BGR)
            imageSid = cv2.cvtColor(imageSid, cv2.COLOR_GRAY2BGR)

            # Label images
            imageToShowTop = imageTop.copy()
            labelTopViewFrame(imageToShowTop, poseEstFromTop)
            imageToShowSid = imageSid.copy()
            labelTopViewFrame(imageToShowSid, poseEstFromSid)

            # display images
            cv2.imshow("TopView", imageToShowTop)
            cv2.imshow("SideView", imageToShowSid)
            key = cv2.waitKey(1)
            if key == ord('q') or key == 27: raise KeyboardInterrupt

            if doSaveVideo:
                topOut.write(imageTop)
                sidOut.write(imageSid)
            
            # show current status on the terminal
            inferenceTime = (time.time() - currCycleStart)
            resultingFPS = resultingFPSNode.GetValue()
            
            if ncursesDisplay is True and frameCnt%5 == 0:
                stdscr.addstr( 0, 0, "Frame number = %8d, Maximum Frame = %8d" % (frameCnt, maxExpFrameNum))
                stdscr.addstr( 1, 0, "\t Acquisition Resulting Frame Rate: %.1f" % resultingFPS)
                stdscr.addstr( 2, 0, "\t Inference Time: %.4f, Loop Time: %.4f, LPS: %.1f" % (inferenceTime, cycleTime, 1/cycleTime))
                for i, (key, node) in enumerate(bufferStatusNode.items()):
                    stdscr.addstr(i+3, 0, "\t\t %s = %d" % (key, node.GetValue()))
                stdscr.addstr( 9, 0, "================================================================================")
                stdscr.addstr(10, 0, "  Part  |  X Coor  |  Y Coor  | Likelyhood")
                stdscr.addstr(11, 0, "----------------------------------------------")
                stdscr.addstr(12, 0, "  Nose  |  %6.2f  |  %6.2f  |  %6.2f  " % (poseEstFromTop[0,0], poseEstFromTop[0,1], poseEstFromTop[0,2]))
                stdscr.addstr(13, 0, "  LEye  |  %6.2f  |  %6.2f  |  %6.2f  " % (poseEstFromTop[1,0], poseEstFromTop[1,1], poseEstFromTop[1,2]))
                stdscr.addstr(14, 0, "  REye  |  %6.2f  |  %6.2f  |  %6.2f  " % (poseEstFromTop[2,0], poseEstFromTop[2,1], poseEstFromTop[2,2]))
                stdscr.addstr(15, 0, "  Body  |  %6.2f  |  %6.2f  |  %6.2f  " % (poseEstFromTop[3,0], poseEstFromTop[3,1], poseEstFromTop[3,2]))
                stdscr.addstr(16, 0, "  Tail  |  %6.2f  |  %6.2f  |  %6.2f  " % (poseEstFromTop[4,0], poseEstFromTop[4,1], poseEstFromTop[4,2]))
                stdscr.addstr(17, 0, "================================================================================")
                stdscr.addstr(18, 0, "To terminate the experiment, press \'Ctrl + C\' or \'q\'.")
                stdscr.refresh()
                        
            # save all the matrix
            poses[frameCnt] = poseEst
            poses_sid[frameCnt] = poseSid
            times[frameCnt] = [inferenceTime, cycleTime, 1/cycleTime, resultingFPS,currCycleStart]

            frameCnt += 1
        
        if ncursesDisplay is True: cleanupCurses(stdscr)
        return True

    except PySpin.SpinnakerException as ex:
        if ncursesDisplay is True: cleanupCurses(stdscr)
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False
    except KeyboardInterrupt as ex:
        if ncursesDisplay is True: cleanupCurses(stdscr)
        logger.info("Catch KeyboardInterrupt, user aborted the acquisition loop.")
        return True
    except Exception as ex:
        if ncursesDisplay is True: cleanupCurses(stdscr)
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False
    
    finally:
        poses = poses[~np.all(poses == 0, axis=1)]
        poses_sid = poses_sid[~np.all(poses_sid == 0, axis=1)]
        times = times[~np.all(times == 0, axis=1)]

        pd.DataFrame(poses, columns=["NoseX", "NoseY", "NoseLikelyhood",\
                                     "LeyeX", "LeyeY", "LeyeLikelyhood",\
                                     "ReyeX", "ReyeY", "ReyeLikelyhood",\
                                     "BodyX", "BodyY", "BodyLikelyhood",\
                                     "TailX", "TailY", "TailLikelyhood",\
                                     ]).to_csv(expCfg.getProjectNameFromCfg() + "_poses.csv")
        pd.DataFrame(poses_sid, columns=["NoseX", "NoseY", "NoseLikelyhood",\
                                     "LeyeX", "LeyeY", "LeyeLikelyhood",\
                                     "ReyeX", "ReyeY", "ReyeLikelyhood",\
                                     "BodyX", "BodyY", "BodyLikelyhood",\
                                     "TailX", "TailY", "TailLikelyhood",\
                                     ]).to_csv(expCfg.getProjectNameFromCfg() + "_posesSid.csv")
        pd.DataFrame(times, columns=["inferenceTime", "CycleTime", "CycleFPS",\
                                     "resultingFps","PythonTime"]).to_csv(expCfg.getProjectNameFromCfg() + "_times.csv")

        cams['top'].EndAcquisition()
        cams['sid'].EndAcquisition()
        udpSocket.cleanUpSocket()
        udpSocket_2.cleanUpSocket()
        if doSaveVideo:
            topOut.release()
            sidOut.release()
        cv2.destroyAllWindows()


def initializeDeepLabCutLive(cams):
    logger.info('About to initialize deeplabcut live model...')

    # Set deeplabcut-live parameters
    if expCfg.isDlcModelExist() is False:
        logger.error("No DeepLabCut model was founded.")
        return None, False
    dlcLive = dlclive.DLCLive(expCfg.getDlcModelDirectoryFromCfg(), processor=dlcProc)
    dlcLive_2 = dlclive.DLCLive(expCfg.getDlcModelDirectoryFromCfg(), processor=dlcProc)
    image, ret = acquireSingleImage(cams["top"])
    if ret is not True: return ret
    print('\n >>>>>>>> Output from tensorflow >>>>>>>>')
    dlcLive.init_inference(image)
    print(' <<<<<<<< Output from tensorflow <<<<<<<< \n')
    dlcLive.get_pose(image)
    logger.debug('Initializing DLC live model finished.')

    image_2, ret = acquireSingleImage(cams["sid"])
    if ret is not True: return ret
    print('\n >>>>>>>> Output from tensorflow >>>>>>>>')
    dlcLive_2.init_inference(image_2)
    print(' <<<<<<<< Output from tensorflow <<<<<<<< \n')
    dlcLive_2.get_pose(image_2)
    logger.debug('Initializing DLC live model finished.')
    
    return dlcLive,dlcLive_2, True

def setImageReverse(cam: PySpin.CameraBase) -> bool:
    logger.info('About to reverse X and Y axis in top view.')
    nodemap: PySpin.INodeMap = cam.GetNodeMap()
    try:
        nodeReverseX = PySpin.CBooleanPtr(nodemap.GetNode('ReverseX'))
        if not PySpin.IsAvailable(nodeReverseX) or not PySpin.IsWritable(nodeReverseX):
            logger.error("During setImageReverse, unable to retrieve or set reverseX node.")
            return False
        nodeReverseX.SetValue(True)
        logger.debug("Top camera: ReverseX has set to True.")

        nodeReverseY = PySpin.CBooleanPtr(nodemap.GetNode('ReverseY'))
        if not PySpin.IsAvailable(nodeReverseY) or not PySpin.IsWritable(nodeReverseY):
            logger.error("During setImageReverse, unable to retrieve or set reverseY node.")
            return False
        nodeReverseY.SetValue(True)
        logger.debug("Top camera: ReverseY has set to True.")
        return True
    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False


def configExposureAndGain(cams) -> bool:
    cfgExposureTime = expCfg.getExposureTimeFromCfg()
    logger.info('About to set exposure time, exposure auto mode and gain auto mode.')

    for i, (key, cam) in enumerate(cams.items()):
        logger.debug('About to set {} camera: ExpoTime {}, ExpoAuto {}, GainAuto {}.'\
                        .format(key, cfgExposureTime[key], 'Off', 'Once'))
        ret = setExposureAutoMode(cam, mode='Off', camName=key)
        if ret is not True: return ret
        ret = setExposureTime(cam, cfgExposureTime[key], camName=key)
        if ret is not True: return ret
        ret = setGainAutoMode(cam, mode='Once', camName=key)
        if ret is not True: return ret
    return True


def configFramerate(cams) -> bool:
    cfgFramerate = expCfg.getAcqFrameRateFromCfg()
    logger.info('About to set acquisition frame rate to %.1f.' % cfgFramerate)

    for i, (key, cam) in enumerate(cams.items()):
        ret = setAcquisitionFrameRate(cam, cfgFramerate, camName=key)
        if ret is not True: return ret
    return True


def configAcquisitionMode(cams) -> bool:
    logger.info('About to set acquisition mode to Continuous mode.')

    for i, (key, cam) in enumerate(cams.items()):
        ret = setAcquisitionMode(cam, 'Continuous', camName=key)
        if ret is not True: return ret
    return True


def configStreamBufferCount(cams) -> bool:
    logger.info('About to set stream buffer count to half maximum.')

    for i, (key, cam) in enumerate(cams.items()):
        ret = setStreamBufferCountMode(cam, 'Manual', camName=key)
        if ret is not True: return ret
        
        ret = setStreamBufferCountToHalfMax(cam)
        if ret is not True: return ret

    return True


def configBufferHandlingMode(cams) -> bool:
    cfgBufferHandlingMode = expCfg.getStreamBufferHandlingModeFromCfg()
    logger.info('About to set buffer handling mode to %s...' % cfgBufferHandlingMode)

    for i, (key, cam) in enumerate(cams.items()):
        ret = setBufferHandlingMode(cam, cfgBufferHandlingMode, camName=key)
        if ret is not True: return ret
    
    return True


def initializeRoi(cams) -> bool:
    logger.info("About to initialize ROI...")
    if expCfg.doReadRoiFromCfg():
        logger.info("Read ROI from config file.")
        for i, (key, cam) in enumerate(cams.items()):
            rect = expCfg.getRegionOfInterestFromCfg()[key]
            roi, ret = adjustRoiByIncrement(cam, rect)
            ret = setCameraRoi(cam, roi, camName=key)
            if ret is False: return ret
    
    else:
        for i, (key, cam) in enumerate(cams.items()):
            isResultGood = False
            while isResultGood is not True:
                print("\t This is the {} view, please select the region you want to acquire.".format(key))
                # Reset the ROI to full-frame before setting a new one
                ret = setCameraRoiToFullFrame(cam, camName=key)
                if ret is not True: return ret

                image, ret = acquireSingleImage(cam)
                if ret is not True: return ret

                # [0]: x, [1]: y, [2]: w, [3]: h
                rect = cv2.selectROI("selectROI", image, showCrosshair=True, fromCenter=False)
                cv2.destroyWindow("selectROI")
                
                roi, ret = adjustRoiByIncrement(cam, rect)
                ret = setCameraRoi(cam, roi, camName=key)
                if ret is False: return ret

                image, ret = acquireSingleImage(cam)
                if ret is not True: return ret
                print('Please check the frame size, press y or Esc to re-select the region, press the others key to continue.')
                cv2.imshow("CheckROI", image)
                keyboardInput = cv2.waitKey(0)
                if keyboardInput != ord('y') and keyboardInput != 27:
                    isResultGood = True

                cv2.destroyWindow("CheckROI")

            expCfg.setCurrentRoiToCfg({key:roi})
    
    logger.info('The region of interest for both cameras are set to:')
    for i, (key, roi) in enumerate(expCfg.getRegionOfInterestFromCfg().items()):
        logger.info('\t {} view: x {}, y {}, w {}, h{}'.format(key, roi[0], roi[1], roi[2], roi[3]))

    return True


def checkCameraExists(camSerial, camList) -> bool:
    logger.info('About to check the camera avability...')
    try:
        # Retrieve the serial number list of all cameras.
        camInList = list()
        for i, cam in enumerate(camList):
            nodeSN, ret = getCameraDeviceSerialNumber(cam)
            if ret is not True: return ret    
            camInList.append(nodeSN)

        # Check the cameras sn listed in the config file are presented or no.
        for i, (key, sn) in enumerate(camSerial.items()):
            if sn not in camInList:
                logger.error("Camera {} is not there, please check!".format(sn))
                return False
        return True
    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False


def main() -> bool:
    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()
    # Retrieve list of cameras from the system
    camList = system.GetCameras()
    cams = dict()

    try:
        if camList.GetSize() == 0:
            logger.error("No camera was detected!")
            return False
        else:
            logger.debug('Number of cameras detected: %d' % camList.GetSize())

        # Identify cameras
        camForExp = expCfg.getCameraSerialNumFromCfg()
        ret = checkCameraExists(camForExp, camList)
        if ret is not True: return ret

        cams = {'top': camList.GetBySerial(camForExp['top']),\
                'sid': camList.GetBySerial(camForExp['sid'])}

        #cams = {'top': camList.GetBySerial(camForExp['top'])}
        
        # Initialize cameras
        cams['top'].Init()
        cams['sid'].Init()

        ret = initializeRoi(cams)
        if ret is not True: return ret

        ret = configBufferHandlingMode(cams)
        if ret is not True: return ret

        ret = configStreamBufferCount(cams)
        if ret is not True: return ret

        ret = configAcquisitionMode(cams)
        if ret is not True: return ret

        ret = configFramerate(cams)
        if ret is not True: return ret

        ret = configExposureAndGain(cams)
        if ret is not True: return ret

        ret = setImageReverse(cams['sid'])
        if ret is not True: return ret

        dlcLive, dlcLive_2, ret = initializeDeepLabCutLive(cams)
        if ret is not True: return ret

        ret = acquireAndDisplayImages(cams, dlcLive, dlcLive_2)
        if ret is not True: return ret

        return True
        
    except Exception as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False

    finally:
        logger.info('About to clean up, clear the camera instances, camera list and release system instance.')
        for cam in camList:
            if cam.IsInitialized() is True:
                cam.DeInit()
        del cam, cams               # remember to del the enumerator (cam)
        camList.Clear()             # Clear camera list before releasing system
        system.ReleaseInstance()    # Release system instance
        oldLogPath = Path.cwd() / 'debug.log'
        newLogPath = Path.cwd() / (expCfg.getProjectNameFromCfg() + '.log')
        os.rename(oldLogPath, newLogPath)
        input('\nClean up process finished! Press Enter to exit...' )
                      
                                                            

if __name__ == '__main__':
    if main() is True:
        logger.info('Normal termination...')
        sys.exit(0)
    else:
        logger.warning("Error termination, please check the debug file!")
        sys.exit(1)
