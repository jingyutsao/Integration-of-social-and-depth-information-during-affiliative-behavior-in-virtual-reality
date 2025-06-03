import PySpin
import cv2
import sys

import numpy as np

import Utils.CamUtils as CamUtils
from MyLogger import logger


def calculateCmToPxRatio(bkImages: dict, refImages: dict, refWidth: float):
    cmToPxRatio = dict()
    logger.info("About to calculate centimeter to pixel ratio...")
    for key in bkImages:
        subFrame = cv2.absdiff(bkImages[key], refImages[key])
        blurFrame = cv2.medianBlur(subFrame, 5)
        isResultGood = False
        while isResultGood is not True:
            thresholdRatio = input("Please enter the binarize threshold ratio [0-1]")
            try:
                thresholdRatio = float(thresholdRatio)
            except ValueError:
                print("Please enter a floating point number within the range of 0 - 1.")
                continue
            if thresholdRatio > 1.0 or thresholdRatio < 0.0: continue
            ret, binFrame = cv2.threshold(blurFrame, np.amax(blurFrame)*thresholdRatio, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(binFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) != 0:
                c = max(contours, key = cv2.contourArea)
                imageWithContour = cv2.cvtColor(refImages[key], cv2.COLOR_GRAY2BGR)
                cv2.drawContours(imageWithContour, c, -1, (0,255,0), 3)
                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(imageWithContour, (x, y), (x+w, y+h), (0, 0, 255), 3)

                print("Please check the image, press n or Esc to retake an image, press the others key to continue...")
                cv2.imshow('BinarizedImage', binFrame)
                cv2.imshow('ScaleObjectContour', imageWithContour)
                keyboardInput = cv2.waitKey(0)
                cv2.destroyWindow('BinarizedImage')
                cv2.destroyWindow('ScaleObjectContour')
                if keyboardInput != ord('n') and keyboardInput != 27:
                    cmToPxRatio[key] = refWidth/w
                    logger.info("The cm to pixel ratio at camera {} is: {}".format(key, cmToPxRatio[key]))
                    isResultGood = True
    return cmToPxRatio
        



def acquireImageWithScaleRef(cams: dict, bkImages: dict):
    refImages = dict()
    logger.info("About to acquire images with scale reference...")
    for key, cam in cams.items():
        try:
            print("About to take photo from this camera, please put your reference object...")
            print("Press any key to continue....")
            cv2.imshow('ShowBackgroundImage', bkImages[key])
            keyboardInput = cv2.waitKey(0)
            cv2.destroyWindow('ShowBackgroundImage')

            isResultGood = False
            while isResultGood is not True:
                refImage, ret = CamUtils.acquireSingleImage(cam)
                if ret is not True: return None, ret
                print("Please check the image, press n or Esc to retake an image, press the others key to continue...")
                cv2.imshow('ReferenceObjectImage', refImage)
                keyboardInput = cv2.waitKey(0)
                if keyboardInput != ord('n') and keyboardInput != 27:
                    refImages[key] = refImage
                    isResultGood = True
                cv2.destroyWindow('ReferenceObjectImage')
        finally:
            cv2.destroyAllWindows()
    
    return refImages, True


def acquireBackgroundImage(cams: dict):
    bkFrameNum = 300            # 5 s
    bkImages = dict()
    logger.info('About to generate the background image...')
    for key, cam in cams.items():
        try:
            imageBuffer = np.zeros((bkFrameNum, 1024, 1280), dtype=np.uint8)
            cam.BeginAcquisition()
            for i in range(bkFrameNum):
                image = cam.GetNextImage(1000)
                if image.IsIncomplete():
                    logger.warning('An image is incomplete with image status %d ...' % image.GetImageStatus())
                    i -= 1
                    continue
                imageBuffer[i] = image.GetNDArray()
                if (i+1) % (bkFrameNum/20) == 0: print('\t Background frame recording process: {} %'\
                    .format(int((i+1)/bkFrameNum*100)))
            bkImages[key] = np.median(imageBuffer, axis=0).astype('uint8')
            print('\t Please check the background image, press n or Esc if something is wrong.')
            cv2.imshow("CheckBackground", bkImages[key])
            keyboardInput = cv2.waitKey(0)
            if keyboardInput == ord('n') or keyboardInput == 27:
                logger.info("During acquireBackgroundImage, user rejected the calculated background.")
                return None, False
        finally:
            cam.EndAcquisition()
            cv2.destroyAllWindows()
    return bkImages, True


def configExposureAndGainToFullAuto(cams: dict):
    expoAuto = 'Once'
    gainAuto = 'Once'

    logger.info('About to set exposure auto mode and gain auto mode.')
    for key, cam in cams.items():
        logger.debug('About to set {} camera: ExpoAuto {}, GainAuto {}.'\
                        .format(key, expoAuto, gainAuto))
        ret = CamUtils.setExposureAutoMode(cam, mode=expoAuto, camName=key)
        if ret is not True: return ret
        ret = CamUtils.setGainAutoMode(cam, mode=gainAuto, camName=key)
        if ret is not True: return ret
    return True


def configAcquisitionModeToContinue(cams: dict):
    logger.info('About to set acquisition mode to Continuous mode.')
    for key, cam in cams.items():
        ret = CamUtils.setAcquisitionMode(cam, 'Continuous', camName=key)
        if ret is not True: return ret
    return True


def configFramerate(cams: dict):
    logger.info('About to set acquisition frame rate to 60.0 Hz.')
    for key, cam in cams.items():
        ret = CamUtils.setAcquisitionFrameRate(cam, 60.0, camName=key)
        if ret is not True: return ret
    return True


def configRoiToFullFrame(cams: dict) -> bool:
    logger.info("About to initialize ROI...")
    for key, cam in cams.items():
        ret = CamUtils.setCameraRoiToFullFrame(cam, camName=key)
        if ret is not True: return ret
    return True


def initializeCameraInUse(camList: PySpin.CameraList, cams: dict) -> bool:
    logger.info("Select cameras in use and initialize them")
    for cam in camList:
        serialNum, ret = CamUtils.getCameraDeviceSerialNumber(cam)
        if ret is not True: return ret
        print("Get camera {}, do you want to set it?".format(serialNum))
        
        while True:
            c = input("\t Enter 'y' to initialize this camera, enter 'n' to skip...\n")
            if c == 'y' or c == 'Y':
                cams[serialNum] = cam
                cam.Init()
                logger.debug("Initialize camera: {}".format(serialNum))
                break
            elif c == 'n' or c == 'N': break
            else: continue

    return True


def main() -> bool:
    system: PySpin.SystemPtr   = PySpin.System.GetInstance()
    camList: PySpin.CameraList = system.GetCameras()
    cams = dict()
    try:
        # Identify cameras
        ret = initializeCameraInUse(camList, cams)
        if ret is not True: return ret

        ret = configRoiToFullFrame(cams)
        if ret is not True: return ret

        ret = configFramerate(cams)
        if ret is not True: return ret
        
        ret = configAcquisitionModeToContinue(cams)
        if ret is not True: return ret

        ret = configExposureAndGainToFullAuto(cams)
        if ret is not True: return ret

        bkImages, ret = acquireBackgroundImage(cams)
        if ret is not True: return ret

        refImages, ret = acquireImageWithScaleRef(cams, bkImages)
        if ret is not True: return ret

        cmToPxRatio = calculateCmToPxRatio(bkImages, refImages, 5.68)

        print(cmToPxRatio)

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
        input('\nClean up process finished! Press Enter to exit...')


if __name__ == '__main__':
    if main() is True:
        logger.info('Normal termination...')
        sys.exit(0)
    else:
        logger.error("Error termination, please check the debug file!")
        sys.exit(1)