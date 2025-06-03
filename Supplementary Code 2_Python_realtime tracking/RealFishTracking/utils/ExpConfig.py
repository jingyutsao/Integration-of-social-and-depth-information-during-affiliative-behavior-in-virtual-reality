import os
import sys
import time
import numpy        as np
from pathlib        import Path
from ruamel.yaml    import YAML

from RealFishTracking.utils.MyLogger       import logger

class ExpConfig(object):
    def __new__(cls):
        """
        Overriding __new__, make ExpConfig a singleton instance
        Returns:
            ExpConfig: Instance of ExpConfig
        """        
        if not hasattr(cls, 'instance'):
            cls.instance = super(ExpConfig, cls).__new__(cls)
        return cls.instance


    def __init__(self) -> None:
        """
        If there is a config file, load it. Otherwise, create one.
        """
        logger.info('About to initialize the experiment...')
        self.cfgPath = Path.cwd() / 'config_video.yml'

        if self.cfgPath.exists() is not True:
            logger.warning('\t No config file was founded, about to create one...')
            self.__createConfigTemplate()
            logger.info('\t Config template generated, the file is located at:\n\t\t %s' % self.cfgPath)
            logger.info('\t Please go to the config file and change wherever you want.')
            logger.info('\t After updating the config file, press any key to continue......')
            input()
        
        logger.info('Config file founded, about to read.')
        self.config = self.readConfigFile(self.cfgPath)
        # initialize variables
        self.sidBkImage = None


    def readConfigFile(self, cfgPath) -> dict:
        yaml = YAML()
        with open(cfgPath, 'r') as file:
            config = yaml.load(file)
            logger.info('Finish loading YML file')
            return config


    def writeConfigFile(self) -> None:
        logger.info('\nAbout to write current config back to file.')
        yaml = YAML()
        with open(self.cfgPath, 'w') as file:
            yaml.dump(self.config, file)


    def __createConfigTemplate(self) -> None:
        yamlStr = \
"""
# Project management
Date: 'yyyy-mm-dd'
Task: ''

# Camera serial number, quote the S/N to ensure it is a string
CameraSerialNum:
    top: '20311290'
    sid: '20406688'
RegionOfInterest:  # [0]: x, [1]: y, [2]: w, [3]: h
    top: [0, 0, 0, 0]
    sid: [0, 0, 0, 0]
ReadROIFromFile: False    # True: Use the above ROI setting, False: Select ROI in the program
ExposureTime:
    top: 5882
    sid: 5882
CentimeterToPixelRatio:
    top: 1.23
    sid: 4.56

# Acquisition setup
AcquisitionFrameRate: 30.0
StreamBufferHandlingMode: 'OldestFirst'
MaximumFrameNumber: 108000

# Pose estimation parameters
# Top View: DeepLabCut-live
DoAnalyzeTopImage: True
DLCModelDir: ''
# Side View: Center of mass
DoAnalyzeSidImage: True
BackgroundFrameNum: 300
BinarizeThreshold: 50

# Video Output
DoSaveVideo: False
"""
        yaml = YAML()
        yamlContent = yaml.load(yamlStr)
        with open(self.cfgPath, 'w') as file:
            yaml.dump(yamlContent, file)


    def getProjectNameFromCfg(self) -> str:
        expDate = time.strptime(self.config['Date'], "%Y-%m-%d")
        return str("{} {}").format(time.strftime('%d%b%Y', expDate), self.config['Task'])


    def getCameraSerialNumFromCfg(self) -> dict:
        return self.config['CameraSerialNum']


    def getRegionOfInterestFromCfg(self) -> dict:
        return self.config['RegionOfInterest']


    def doReadRoiFromCfg(self) -> bool:
        return self.config['ReadROIFromFile']


    def getCmToPxRatioFromCfg(self) -> dict:
        return self.config['CentimeterToPixelRatio']

    
    def getAcqFrameRateFromCfg(self) -> float:
        return self.config['AcquisitionFrameRate']


    def getExposureTimeFromCfg(self) -> dict:
        return self.config['ExposureTime']


    def getStreamBufferHandlingModeFromCfg(self) -> str:
        return self.config['StreamBufferHandlingMode']


    def getMaximumExperimentFrameNum(self) -> int:
        return self.config['MaximumFrameNumber']


    def getSideViewBackgroundFrameNum(self) -> int:
        return self.config['BackgroundFrameNum']


    def getDlcModelDirectoryFromCfg(self) -> str:
        return self.config['DLCModelDir']


    def doAnalyzeTopViewImage(self) -> bool:
        return self.config['DoAnalyzeTopImage']


    def doAnalyzeSidViewImage(self) -> bool:
        return self.config['DoAnalyzeSidImage']


    def doSaveVideo(self) -> bool:
        return self.config['DoSaveVideo']


    def setCurrentRoiToCfg(self, roi) -> None:
        self.config['RegionOfInterest'].update(roi)


    def setSideViewBackground(self, image) -> None:
        self.sidBkImage = image


    def getSideViewBackground(self) -> np.array:
        return self.sidBkImage


    def isDlcModelExist(self) -> bool:
        dlcModelPath = Path.cwd() / self.config['DLCModelDir']
        return dlcModelPath.exists()

# Instantiate an experiment config handler immediately when importing this module
expCfg = ExpConfig()