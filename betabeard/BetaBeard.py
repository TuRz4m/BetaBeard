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
logging.getLogger(__name__).setLevel(logging.INFO)
logging.getLogger(__name__).addHandler(logging.StreamHandler())
logging.getLogger(__name__).addHandler(logging.FileHandler("logs/BetaBeard.log"))



configFile = "BetaBeard.ini"
configDbFile = "BetaBeard.db"
param = {}
paramDb = {}


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

    except ConfigParser.NoOptionError as ex:
        logger.error("[BetaBeard] Error in config file : %s", ex)
        return False
    except ConfigParser.NoSectionError as ex:
        logger.error("[BetaBeard] Error in config file : %s", ex)
        return False

    return True



def loadDb(configToLoad):
    global paramDb

    if (os.path.exists(configDbFile)):
        configToLoad.read(configDbFile)

    try:
        paramDb['last_event_id'] = configToLoad.get("BetaBeard", "last_event_id")
        if (paramDb['last_event_id'] == ""):
            paramDb['last_event_id'] = None
    except ConfigParser.NoOptionError:
        logger.debug("[BetaBeard] Config file Tech not found. Use default.")
        paramDb['last_event_id'] = None
    except ConfigParser.NoSectionError:
        logger.debug("[BetaBeard] Config file Tech not found. Use default.")
        configToLoad.add_section("BetaBeard")
        paramDb['last_event_id'] = None





"""
Update the BetaBeard-tech.ini
"""
def updateDb(configToSave):
    logger.debug("[BetaBeard] Update file %s", configDbFile)
    cfgfile = open(configDbFile,'w')
    configToSave.write(cfgfile)
    cfgfile.close()
    logger.debug("[BetaBeard] File %s updated.", configDbFile)









if __name__ == '__main__':
    # First of all, we need to reed the BetaBeard.ini config file.
    config = ConfigParser.SafeConfigParser()
    configDb = ConfigParser.SafeConfigParser()

    if (os.path.exists(configFile) == False):
        logger.error("[BetaBeard] Config file %s not found.", configFile)
        sys.exit(0)

    config.read(configFile)
    loadDb(configDb)

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

    # ----------- If fullUpdate, we retrieve all the current show and add them to sickbear.----------- #
    if paramDb['last_event_id'] == None:
        logger.debug("[BetaBeard] last_index_id is None")
        if param['fullUpdate'] == True:
            shows = beta.show_list();
            logger.debug("[BetaBeard] shows : %s", shows)
            for show in shows:
                logger.info("[BetaBeard] Add show in SickBeard : %s", show)
                success = sickBeard.add_show(show, param['location'],  param['lang'],  param['flatten_folder'],  param['status'],  param['initial'],  param['archive'])
                if (success == False):
                    logger.error("[BetaBeard] Can't add show %s to sickbeard.", show)

        # ----------- retrieve last  event processed in betaseries----------- #
        param['last_event_id'], emptyList = beta.timeline_since(None)
    else:
        param['last_event_id'], events = beta.timeline_since(paramDb['last_event_id'])
        logger.debug("[BetaBeard] Processing timeline : %s", events)
        for event in events:
            logger.debug("[BetaBeard] Event : %s", event)
            if (event['type'] == 'add_serie'):
                logger.info("[BetaBeard] Add Show to sickbeard : %s", event['ref_id'])
            elif (event['type'] == 'del_serie'):
                logger.info("[BetaBeard] Delete Show from sickbeard : %s", event['ref_id'])
            elif (event['type'] == 'archive'):
                logger.info("[BetaBeard] Archive Show on sickbeard : %s", event['ref_id'])
            elif (event['type'] == 'unarchive'):
                logger.info("[BetaBeard] UnArchive Show on sickbeard : %s", event['ref_id'])





    # ----------- Update Last_event_id in config file.----------- #
    if (param['last_event_id'] != None):
        logger.info("[BetaBeard] update config with last_event_id=%s", param['last_event_id'])
        configDb.set("BetaBeard", "last_event_id", str(param['last_event_id']));
        updateDb(configDb);
    else:
        logger.info("[BetaBeard] Can't update config file because last_event_id is null")





