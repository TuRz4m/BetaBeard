'''
Created on 10 dec. 2013

@author: TuRz4m
'''
import ConfigParser
import logging
import sys
from api.APIUtils import BetaSerieAPI, BadLoginException
import os.path


logger = logging.getLogger(__name__)
logging.getLogger(__name__).addHandler(logging.StreamHandler())
logging.getLogger(__name__).addHandler(logging.FileHandler("logs/BetaBeard.log"))
logging.getLogger(__name__).setLevel(logging.INFO)


configFile = "BetaBeard.ini"

def checkConfig(config):
    try:
        config.get("BetaSeries", "login")
        config.get("BetaSeries", "password")
        config.get("SickBeard", "url")
        config.getboolean("SickBeard", "https")
        config.get("SickBeard", "apikey")
    except ConfigParser.NoOptionError as ex:
        logger.error("[BetaBeard] Error in config file : %s", ex)
        return False
    except ConfigParser.NoSectionError as ex:
        logger.error("[BetaBeard] Error in config file : %s", ex)
        return False

    return True

def createIni(config):
    logger.debug("[BetaBeard] Create file %s", configFile)
    cfgfile = open(configFile,'w')

    config.add_section('BetaSeries')
    config.set('BetaSeries','login', "Dev047")
    config.set('BetaSeries','password', "developer")

    config.add_section('SickBeard')
    config.set('SickBeard','url', "localhost:8081")
    config.set('SickBeard','https', "True")
    config.set('SickBeard','apikey', "")

    config.write(cfgfile)
    cfgfile.close()
    logger.debug("[BetaBeard] File %s created.", configFile)












if __name__ == '__main__':
    # First of all, we need to reed the BetaBeard.ini config file.
    config = ConfigParser.SafeConfigParser()

    if (os.path.exists(configFile) == False):
        createIni(config)
        logger.error("[BetaBeard] Config file %s not found.", configFile)
        sys.exit(0)

    config.read(configFile)

    if checkConfig(config) == False:
        sys.exit(0)

    try:
        beta = BetaSerieAPI(config.get("BetaSeries", "login"), config.get("BetaSeries", "password"))
    except BadLoginException as ex:
        logger.error("[BetaBeard] can't log into BetaSeries.com : %s", ex.value['text'])




