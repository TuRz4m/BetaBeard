'''
Created on 10 dec. 2013

@author: TuRz4m
'''
import ConfigParser
import logging
import sys
from api.APIUtils import BetaSerieAPI, BadLoginException, SickBeardAPI
import os.path


logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)
logging.getLogger(__name__).addHandler(logging.StreamHandler())
logging.getLogger(__name__).addHandler(logging.FileHandler("logs/BetaBeard.log"))



configFile = "BetaBeard.ini"
param = {}


"""
Load the config file & fill all the var.
"""
def checkConfig(config):
    try:
        global param

        param['login'] = config.get("BetaSeries", "login")
        param['password'] = config.get("BetaSeries", "password")

        param['sburl'] = config.get("SickBeard", "url")
        if (config.getboolean("SickBeard", "https")):
            param['scheme'] = "https"

        param['apikey'] = config.get("SickBeard", "apikey")


        param['location'] = config.get("SickBeard", "location")
        if (param['location'] == ""):
            param['location'] = None
        param['lang'] = config.get("SickBeard", "lang")
        if (param['lang'] == ""):
            param['lang'] = None
        param['flatten_folder'] = config.get("SickBeard", "flatten_folder")
        if (param['flatten_folder'] == ""):
            param['flatten_folder'] = None
        param['status'] = config.get("SickBeard", "status")
        if (param['status'] == ""):
            param['status'] = None
        param['initial'] = config.get("SickBeard", "initial")
        if (param['initial'] == ""):
            param['initial'] = None
        param['archive'] = config.get("SickBeard", "archive")
        if (param['archive'] == ""):
            param['archive'] = None

        param['fullUpdate'] = config.get("BetaBeard", "fullUpdate")
        param['last_event_id'] = config.get("BetaBeard", "last_event_id")
        if (param['last_event_id'] == ""):
            param['last_event_id'] = None

    except ConfigParser.NoOptionError as ex:
        logger.error("[BetaBeard] Error in config file : %s", ex)
        return False
    except ConfigParser.NoSectionError as ex:
        logger.error("[BetaBeard] Error in config file : %s", ex)
        return False

    return True







def createDefault(config):
    config.add_section('BetaSeries')
    config.set('BetaSeries','login', "Dev047")
    config.set('BetaSeries','password', "developer")

    config.add_section('SickBeard')
    config.set('SickBeard','url', "localhost:8081")
    config.set('SickBeard','https', "True")
    config.set('SickBeard','apikey', "")
    config.set("SickBeard", "location", "")
    config.set("SickBeard", "lang", "")
    config.set("SickBeard", "status", "")
    config.set("SickBeard", "intial", "")
    config.set("SickBeard", "archive", "")

    config.add_section('BetaBeard')
    config.set("BetaBeard", "fullUpdate", "True")
    config.set("BetaBeard", "last_index_id", "")

    logger.debug("[BetaBeard] Default value added in config file.")


def updateIni(config):
    logger.debug("[BetaBeard] Update file %s", configFile)
    cfgfile = open(configFile,'w')
    config.write(cfgfile)
    cfgfile.close()
    logger.debug("[BetaBeard] File %s updated.", configFile)









if __name__ == '__main__':
    # First of all, we need to reed the BetaBeard.ini config file.
    config = ConfigParser.SafeConfigParser()

    if (os.path.exists(configFile) == False):
        createDefault(config)
        updateIni(config);
        logger.error("[BetaBeard] Config file %s not found.", configFile)
        sys.exit(0)

    config.read(configFile)

    if checkConfig(config) == False:
        sys.exit(0)

    # ----------- Init BetaSeries ----------- #
    try:
        beta = BetaSerieAPI(param['login'], param['password'])
    except BadLoginException as ex:
        logger.error("[BetaBeard] can't log into BetaSeries.com : %s", ex.value['text'])
        sys.exit(0)

    logger.info("[BetaBeard] Login successfull.")
    # ----------- Init SickBeard ----------- #

    sickBeard = SickBeardAPI(param['sburl'], param['scheme'], param['apikey'])

    # ----------- Test SickBeard ----------- #
    if (sickBeard.ping() == False):
        logger.error("[BetaBeard] Can't ping SickBeard on url : %s://%s with apikey = %s",param['scheme'], param['sburl'], param['apikey'])
        sys.exit(0)
    logger.info("[BetaBeard] Ping SickBeard successfull.")

    # ----------- retrieve last  event processed in betaseries----------- #
    if param['last_event_id'] == None:
        logger.debug("[BetaBeard] last_index_id is None")
        if param['fullUpdate']:
            shows = beta.show_list();
            logger.debug("[BetaBeard] shows : %s", shows)
            for show in shows:
                logger.info("[BetaBeard] Add show in SickBeard : %s", show)
                success = sickBeard.add_show(show, param['location'],  param['lang'],  param['flatten_folder'],  param['status'],  param['initial'],  param['archive'])
                if (success == False):
                    logger.error("[BetaBeard] Can't add show %s to sickbeard.", show)
        param['last_event_id'], emptyList = beta.timeline_since(None)
        if (param['last_event_id'] != None):
            logger.info("[BetaBeard] update config with last_event_id=%s", param['last_event_id'])
            config.set("BetaBeard", "last_event_id", param['last_event_id']);
            updateIni(config);
        else:
            logger.info("[BetaBeard] Can't update config file because last_event_id is null")





