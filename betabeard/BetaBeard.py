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

        param['fullUpdate'] = config.getboolean("BetaBeard", "fullUpdate")
        param['checkTimeLine'] = config.getboolean("BetaBeard", "checkTimeLine")
        param['demoMode'] = config.getboolean("BetaBeard", "demoMode")

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
        logger.error("[BetaBeard] can't log into BetaSeries.com : %s", ex.value)
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
            logger.info("[BetaBeard] Start processing shows.")
            for show in shows:
                logger.info("[BetaBeard] Add show in SickBeard : %s (%s)", show[1], show[0])
                if (param['demoMode'] == False):
                    success,message = sickBeard.add_show(show[0], param['location'],  param['lang'],  param['flatten_folder'],  param['status'],  param['initial'],  param['archive'])
                    if (success == False):
                        logger.error("[BetaBeard] Can't add show %s (%s) to sickbeard : %s", show[1], show[0], message)

        # ----------- retrieve last  event processed in betaseries----------- #
        param['last_event_id'], emptyList = beta.timeline_since(None)
    elif param['checkTimeLine']:
        logger.info("[BetaBeard] Start processing timeline.")
        param['last_event_id'], events = beta.timeline_since(paramDb['last_event_id'])
        logger.debug("[BetaBeard] Processing timeline : %s", events)
        if (events != None):
            for event in events:
                logger.debug("[BetaBeard] Event : %s", event)

                # - ADD SERIE - #
                if (event['type'] == 'add_serie'):
                    betaid = str(event['ref_id']);
                    tvdbid, title = beta.shows_tvdbid(betaid)
                    logger.info("[BetaBeard] Add Show to sickbeard : %s (%s)", title, tvdbid)

                    if (param['demoMode'] == False):
                        success,message = sickBeard.add_show(tvdbid, param['location'],  param['lang'],  param['flatten_folder'],  param['status'],  param['initial'],  param['archive'])
                        if (success == False):
                            logger.error("[BetaBeard] Can't add show %s (%s) to sickbeard : %s.", title, tvdbid, message)

                # - DELETE SERIE - #
                elif (event['type'] == 'del_serie'):
                    betaid = str(event['ref_id']);
                    tvdbid, title = beta.shows_tvdbid(betaid)
                    logger.info("[BetaBeard] Delete Show from sickbeard :  %s (%s)", title, tvdbid)

                    if (param['demoMode'] == False):
                        success, message =  sickBeard.del_show(tvdbid)
                        if (success == False):
                            logger.error("[BetaBeard] Can't delete show %s (%s) from sickbeard : %s.", title, tvdbid, message)

                # - PAUSE SERIE - #
                elif (event['type'] == 'archive'):
                    betaid = str(event['ref_id']);
                    tvdbid, title = beta.shows_tvdbid(betaid)
                    logger.info("[BetaBeard] Archive Show on sickbeard : %s (%s)", title, tvdbid)

                    if (param['demoMode'] == False):
                        success, message =  sickBeard.pause_show(tvdbid, 1)
                        if (success == False):
                            logger.error("[BetaBeard] Can't pause show %s (%s) on sickbeard : %s.", title, tvdbid, message)

                # - UNPAUSE SERIE - #
                elif (event['type'] == 'unarchive'):
                    betaid = str(event['ref_id']);
                    tvdbid, title = beta.shows_tvdbid(betaid)
                    logger.info("[BetaBeard] UnArchive Show on sickbeard :  %s (%s)", title, tvdbid)

                    if (param['demoMode'] == False):
                        success, message =  sickBeard.pause_show(tvdbid, 0)
                        if (success == False):
                            logger.error("[BetaBeard] Can't unpause show %s (%s) on sickbeard : %s.", title, tvdbid, message)

        logger.info("[BetaBeard] Timeline processing done.")





    # ----------- Update Last_event_id in config file.----------- #
    if (param['last_event_id'] != None):
        logger.debug("[BetaBeard] update config with last_event_id=%s", param['last_event_id'])
        configDb.set("BetaBeard", "last_event_id", str(param['last_event_id']));
        updateDb(configDb);
    else:
        logger.debug("[BetaBeard] Can't update config file because last_event_id is null")





