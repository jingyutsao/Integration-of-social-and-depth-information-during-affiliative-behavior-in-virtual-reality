import PySpin
import ctypes

from RealFishTracking.utils.MyLogger import logger


def getCameraDeviceSerialNumber(cam: PySpin.CameraBase):
    try:
        tlNodemap = cam.GetTLDeviceNodeMap()
        nodeSN = PySpin.CStringPtr(tlNodemap.GetNode('DeviceSerialNumber'))
        if not PySpin.IsAvailable(nodeSN) and not PySpin.IsReadable(nodeSN):
            logger.error('Unable to retrieve device serial number node.')
            return None, False
        nodeSN = nodeSN.GetValue()
        return nodeSN, True
    
    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return None, False


def getStreamBufferStatusNodes(cam: PySpin.CameraBase):
    sNodeMap = cam.GetTLStreamNodeMap()
    streamStartedFrameCount = PySpin.CIntegerPtr(sNodeMap.GetNode('StreamStartedFrameCount'))
    if not PySpin.IsAvailable(streamStartedFrameCount) or not PySpin.IsReadable(streamStartedFrameCount):
        logger.error("Unable to retrieve streamStartedFrameCount node.")
        return None, False

    streamDeliveredFrameCount = PySpin.CIntegerPtr(sNodeMap.GetNode('StreamDeliveredFrameCount'))
    if not PySpin.IsAvailable(streamDeliveredFrameCount) or not PySpin.IsReadable(streamDeliveredFrameCount):
        logger.error("Unable to retrieve streamDeliveredFrameCount node.")
        return None, False

    streamLostFrameCount = PySpin.CIntegerPtr(sNodeMap.GetNode('StreamLostFrameCount'))
    if not PySpin.IsAvailable(streamLostFrameCount) or not PySpin.IsReadable(streamLostFrameCount):
        logger.error("Unable to retrieve streamLostFrameCount node.")
        return None, False
    
    streamDropFrameCount = PySpin.CIntegerPtr(sNodeMap.GetNode('StreamDroppedFrameCount'))
    if not PySpin.IsAvailable(streamDropFrameCount) or not PySpin.IsReadable(streamDropFrameCount):
        logger.error("Unable to retrieve streamDroppedFrameCount node.")
        return None, False

    streamInputBufferCount = PySpin.CIntegerPtr(sNodeMap.GetNode('StreamInputBufferCount'))
    if not PySpin.IsAvailable(streamInputBufferCount) or not PySpin.IsReadable(streamInputBufferCount):
        logger.error("Unable to retrieve streamInputBufferCount node.")
        return None, False
    
    streamOutputBufferCount = PySpin.CIntegerPtr(sNodeMap.GetNode('StreamOutputBufferCount'))
    if not PySpin.IsAvailable(streamOutputBufferCount) or not PySpin.IsReadable(streamOutputBufferCount):
        logger.error("Unable to retrieve streamOutputBufferCount node.")
        return None, False
    
    bufferStatusNodes = {'StartedFrameCount':streamStartedFrameCount,\
                         'DeliveredFrameCount':streamDeliveredFrameCount,\
                         'LostFrameCount':streamLostFrameCount,\
                         'DroppedFrameCount':streamDropFrameCount,\
                         'InputBufferCount':streamInputBufferCount,\
                         'OutputBufferCount':streamOutputBufferCount}
    return bufferStatusNodes, True


def getResultingFrameRateNodes(cam: PySpin.CameraBase):
    nodemap = cam.GetNodeMap()
    nodeResultingFramerate = PySpin.CFloatPtr(nodemap.GetNode('AcquisitionResultingFrameRate'))
    if not PySpin.IsAvailable(nodeResultingFramerate) or not PySpin.IsReadable(nodeResultingFramerate):
        logger.error("Unable to retrieve AcquisitionResultingFrameRate node.")
        return None, False
    return nodeResultingFramerate, True


# Methods for setting PySpin.IStreamNodeMap with PySpin.CIntegerPtr
def setStreamBufferCountToHalfMax(cam: PySpin.CameraBase, camName='') -> bool:
    streamNodemap: PySpin.INodeMap = cam.GetTLStreamNodeMap()
    try:
        nodeStreamBufferCount = PySpin.CIntegerPtr(streamNodemap.GetNode('StreamBufferCountManual'))
        if not PySpin.IsAvailable(nodeStreamBufferCount) or not PySpin.IsWritable(nodeStreamBufferCount):
            logger.error("During setStreamBufferCountMode, unable to retrieve/ set StreamBufferCountManual node.")
            return False

        count = int(nodeStreamBufferCount.GetMax()/2)
        nodeStreamBufferCount.SetValue(count)
        logger.debug("{} camera: Stream buffer has been set to {} count.".format(camName, nodeStreamBufferCount.GetValue()))
        return True

    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False


# Methods for setting PySpin.INodeMap with PySpin.CFloatPtr
def setAcquisitionFrameRate(cam: PySpin.CameraBase, framerate: float, camName='') -> bool:
    nodemap: PySpin.INodeMap = cam.GetNodeMap()
    try:
        nodeAcqFramerateEnable = PySpin.CBooleanPtr(nodemap.GetNode('AcquisitionFrameRateEnable'))
        if not nodeAcqFramerateEnable.GetValue():
            if not PySpin.IsAvailable(nodeAcqFramerateEnable) or not PySpin.IsWritable(nodeAcqFramerateEnable):
                logger.error("During setAcquisitionFrameRate, unable to change AcqFramerateEnable node.")
                return False
            nodeAcqFramerateEnable.SetValue(True)
        
        nodeAcqFramerate = PySpin.CFloatPtr(nodemap.GetNode('AcquisitionFrameRate'))
        if not PySpin.IsAvailable(nodeAcqFramerate) or not PySpin.IsWritable(nodeAcqFramerate):
            logger.error("During setAcquisitionFrameRate, unable to set acquisition framerate.")
            return False
        
        nodeAcqFramerate.SetValue(framerate)
        logger.debug("{} camera: Exposure time has been set to {} Hz.".format(camName, nodeAcqFramerate.GetValue()))
        return True

    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False


def setExposureTime(cam: PySpin.CameraBase, expoTime: float, camName='') -> bool:
    nodemap = cam.GetNodeMap()
    try:
        nodeExposureTime = PySpin.CFloatPtr(nodemap.GetNode('ExposureTime'))
        if not PySpin.IsAvailable(nodeExposureTime) or not PySpin.IsWritable(nodeExposureTime):
            logger.error("During setExposureTime, unable to set exposure time.")
            return False
        
        nodeExposureTime.SetValue(expoTime)
        logger.debug("{} camera: Exposure time has been set to {} micorsec.".format(camName, nodeExposureTime.GetValue()))
        return True

    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False


# Methods for setting PySpin.IStreamNodeMap with PySpin.IEnumEntry
def setStreamBufferCountMode(cam: PySpin.CameraBase, mode, camName='') -> bool:
    streamNodemap: PySpin.INodeMap = cam.GetTLStreamNodeMap()
    try:
        nodeStreamBufferMode = PySpin.CEnumerationPtr(streamNodemap.GetNode('StreamBufferCountMode'))
        if not PySpin.IsAvailable(nodeStreamBufferMode) or not PySpin.IsWritable(nodeStreamBufferMode):
            logger.error("During setStreamBufferCountMode, unable to retrieve/ set StreamBufferCountMode node.")
            return False

        nodeMode = PySpin.CEnumEntryPtr(nodeStreamBufferMode.GetEntryByName(mode))
        if not PySpin.IsAvailable(nodeMode) or not PySpin.IsReadable(nodeMode):
            logger.error("During setStreamBufferCountMode, unable to get {} mode entry.".format(mode))
            return False

        nodeStreamBufferMode.SetIntValue(nodeMode.GetValue())
        logger.debug("{} camera: Stream buffer count mode has been set to {} mode.".format(camName, mode))
        return True
        
    except PySpin.SpinnakerException as ex:
        logger.exception(ex)
        return False


def setBufferHandlingMode(cam: PySpin.CameraBase, mode, camName='') -> bool:
    streamNodemap: PySpin.INodeMap = cam.GetTLStreamNodeMap()
    try:
        nodeBuffHandlingMode = PySpin.CEnumerationPtr(streamNodemap.GetNode('StreamBufferHandlingMode'))
        if not PySpin.IsAvailable(nodeBuffHandlingMode) or not PySpin.IsWritable(nodeBuffHandlingMode):
            logger.error("During setStreamBufferCountMode, unable to retrieve/ set StreamBufferHandlingMode node.")
            return False
        
        nodeMode: PySpin.IEnumEntry = nodeBuffHandlingMode.GetEntryByName(mode)
        if not PySpin.IsAvailable(nodeMode) or not PySpin.IsReadable(nodeMode):
            logger.error("During setBufferHandlingMode, unable to get {} mode entry.".format(mode))
            return False
        
        nodeBuffHandlingMode.SetIntValue(nodeMode.GetValue())
        logger.debug("{} camera: Acquisition mode has set to {} mode.".format(camName, mode))
        return True

    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False


# Methods for setting PySpin.INodeMap with PySpin.IEnumEntry
def setAcquisitionMode(cam: PySpin.CameraBase, mode, camName='') -> bool:
    nodemap: PySpin.INodeMap = cam.GetNodeMap()
    try:
        nodeAcqMode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(nodeAcqMode) or not PySpin.IsWritable(nodeAcqMode):
            logger.error("During setAcquisitionMode, unable to retrieve or set AcquisitionMode node.")
            return False
        
        nodeMode: PySpin.IEnumEntry = nodeAcqMode.GetEntryByName(mode)
        if not PySpin.IsAvailable(nodeMode) or not PySpin.IsReadable(nodeMode):
            logger.error("During setAcquisitionMode, unable to get {} mode entry.".format(mode))
            return False
        
        nodeAcqMode.SetIntValue(nodeMode.GetValue())
        logger.debug("{} camera: Acquisition mode has set to {} mode.".format(camName, mode))
        return True

    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False
        

def setExposureAutoMode(cam: PySpin.CameraBase, mode, camName='') -> bool:
    nodemap: PySpin.INodeMap = cam.GetNodeMap()
    try:
        nodeExpoAutoMode = PySpin.CEnumerationPtr(nodemap.GetNode('ExposureAuto'))
        if not PySpin.IsAvailable(nodeExpoAutoMode) or not PySpin.IsWritable(nodeExpoAutoMode):
            logger.error("During setExposureAutoMode, unable to retrieve or set ExposureAuto node.")
            return False
        
        nodeMode: PySpin.IEnumEntry = nodeExpoAutoMode.GetEntryByName(mode)
        if not PySpin.IsAvailable(nodeMode) or not PySpin.IsReadable(nodeMode):
            logger.error("During setExposureAutoMode, unable to get {} mode entry.".format(mode))
            return False
        
        nodeExpoAutoMode.SetIntValue(nodeMode.GetValue())
        logger.debug("{} camera: Exposure auto mode has set to {} mode.".format(camName, mode))
        return True

    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False


def setGainAutoMode(cam: PySpin.CameraBase, mode, camName='') -> bool:
    nodemap: PySpin.INodeMap = cam.GetNodeMap()
    try:
        nodeGainAutoMode = PySpin.CEnumerationPtr(nodemap.GetNode('GainAuto'))
        if not PySpin.IsAvailable(nodeGainAutoMode) or not PySpin.IsWritable(nodeGainAutoMode):
            logger.error("During setGainAutoMode, unable to retrieve or set GainAuto node.")
            return False
        
        nodeMode: PySpin.IEnumEntry = nodeGainAutoMode.GetEntryByName(mode)
        if not PySpin.IsAvailable(nodeMode) or not PySpin.IsReadable(nodeMode):
            logger.error("During setGainAutoMode, unable to get {} mode entry.".format(mode))
            return False
        
        nodeGainAutoMode.SetIntValue(nodeMode.GetValue())
        logger.debug("{} camera: Gain auto mode has set to {} mode.".format(camName, mode))
        return True
    
    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False


# Methods for setting region of interest
def setCameraRoi(cam: PySpin.CameraBase, roi, camName='') -> bool:
    try:
        roiNodes, ret = __getRegionOfInterestNodes(cam)
        if ret is not True: return None, False
        
        # Before adjust offsets, shrink the frame to minimum to avoid OutOfRangeException
        roiNodes['nodeOffsetX'].SetValue(roiNodes['nodeOffsetX'].GetMin())
        roiNodes['nodeOffsetY'].SetValue(roiNodes['nodeOffsetY'].GetMin())

        roiNodes['nodeWidth'].SetValue(roi[2])
        roiNodes['nodeHeight'].SetValue(roi[3])
        roiNodes['nodeOffsetX'].SetValue(roi[0])
        roiNodes['nodeOffsetY'].SetValue(roi[1])
        logger.debug("{} camera: ROI has been set to x={}, y={}, w={}, h={}."\
                        .format(camName, roi[0], roi[1], roi[2], roi[3]))

        return True

    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False


def setCameraRoiToFullFrame(cam: PySpin.CameraBase, camName='') -> bool:
    try:
        roiNodes, ret = __getRegionOfInterestNodes(cam)
        if ret is not True: return None, False
        
        roi = (roiNodes['nodeOffsetX'].GetMin(), roiNodes['nodeOffsetY'].GetMin())
        roiNodes['nodeOffsetX'].SetValue(roi[0])
        roiNodes['nodeOffsetY'].SetValue(roi[1])

        imgSize = (roiNodes['nodeWidth'].GetMax(), roiNodes['nodeHeight'].GetMax())
        roiNodes['nodeWidth'].SetValue(imgSize[0])
        roiNodes['nodeHeight'].SetValue(imgSize[1])
        logger.debug("{} camera: ROI has been set to full frame.(x={}, y={}, w={}, h={})"\
                        .format(camName, roi[0], roi[1], imgSize[0], imgSize[1]))
        return True

    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return False


def adjustRoiByIncrement(cam: PySpin.CameraBase, roi):
    try:
        roiNodes, ret = __getRegionOfInterestNodes(cam)
        if ret is not True: return None, False

        x = roi[0] - roi[0] % roiNodes['nodeOffsetX'].GetInc()
        y = roi[1] - roi[1] % roiNodes['nodeOffsetY'].GetInc()
        w = roi[2]
        if w % roiNodes['nodeWidth'].GetInc() is not 0:
            w = w + (roiNodes['nodeWidth'].GetInc() - w % roiNodes['nodeWidth'].GetInc())
        h = roi[3]
        if h % roiNodes['nodeHeight'].GetInc() is not 0:
            h = h + (roiNodes['nodeHeight'].GetInc() - h % roiNodes['nodeHeight'].GetInc())

        return (x, y, w, h), True
    except PySpin.SpinnakerException as ex:
        logger.critical(ex, exc_info=True)
        logger.exception(ex)
        return None, False


def __getRegionOfInterestNodes(cam: PySpin.CameraBase):
    nodemap: PySpin.INodeMap = cam.GetNodeMap()
    nodeWidth = PySpin.CIntegerPtr(nodemap.GetNode('Width'))
    if not PySpin.IsAvailable(nodeWidth) or not PySpin.IsWritable(nodeWidth):
            logger.error('Unable to retrieve or set Width node.')
            return None, False
    nodeHeight = PySpin.CIntegerPtr(nodemap.GetNode('Height'))
    if not PySpin.IsAvailable(nodeHeight) or not PySpin.IsWritable(nodeHeight):
        logger.error('Unable to retrieve or set Height node.')
        return None, False
    nodeOffsetX = PySpin.CIntegerPtr(nodemap.GetNode('OffsetX'))
    if not PySpin.IsAvailable(nodeOffsetX) or not PySpin.IsWritable(nodeOffsetX):
        logger.error('Unable to retrieve or set OffsetX node.')
        return None, False
    nodeOffsetY = PySpin.CIntegerPtr(nodemap.GetNode('OffsetY'))
    if not PySpin.IsAvailable(nodeOffsetY) or not PySpin.IsWritable(nodeOffsetY):
        logger.error('Unable to retrieve or set OffsetY node.')
        return None, False
    
    roiNodes = {'nodeWidth': nodeWidth, 'nodeHeight':nodeHeight,\
                'nodeOffsetX':nodeOffsetX, 'nodeOffsetY':nodeOffsetY}
    
    return roiNodes, True


# Acquiring single image using singleFrame acquisition mode
def acquireSingleImage(cam: PySpin.CameraBase) -> tuple:
    ret = setAcquisitionMode(cam, 'SingleFrame', "Before single image acquisition, ")
    if ret is not True: return (None, ret)

    cam.BeginAcquisition()
    try:
        image: PySpin.ImagePtr = cam.GetNextImage(1000)
        if image.IsIncomplete():
                logger.error("During acquireSingleImage, image incomplete with image status %d ..."\
                             % image.GetImageStatus())
                return None, False
            
        image = image.GetNDArray()
    finally:
        cam.EndAcquisition()
    
    ret = setAcquisitionMode(cam, 'Continuous', "After single image acquisition, ")
    if ret is not True: return None, ret
    
    return image, True


# Return how many references point to the object
def refCount(obj): return { id(obj): ctypes.c_long.from_address(id(obj)).value}