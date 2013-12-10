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
login =""
password =""
sburl = ""
scheme = "http"
apikey = ""
fullUpdate = True
location = ""
lang = ""
flatten_folder = ""
status = ""
initial = ""
archive = ""
last_index_id = None

def checkConfig(config):
    try:
        global login
        global password
        global sburl
        global scheme
        global apikey
        global fullUpdate
        global location
        global lang
        global flatten_folder
        global status
        global initial
        global archive
        global last_index_id

        login = config.get("BetaSeries", "login")
        password = config.get("BetaSeries", "password")

        sburl = config.get("SickBeard", "url")
        if (config.getboolean("SickBeard", "https")):
            scheme = "https"

        apikey = config.get("SickBeard", "apikey")


        location = config.get("SickBeard", "location")
        if (location == ""):
            location = None
        lang = config.get("SickBeard", "lang")
        if (lang == ""):
            lang = None
        flatten_folder = config.get("SickBeard", "flatten_folder")
        if (flatten_folder == ""):
            flatten_folder = None
        status = config.get("SickBeard", "status")
        if (status == ""):
            status = None
        initial = config.get("SickBeard", "initial")
        if (initial == ""):
            initial = None
        archive = config.get("SickBeard", "archive")
        if (archive == ""):
            archive = None

        fullUpdate = config.get("BetaBeard", "fullUpdate")
        last_index_id = config.get("BetaBeard", "last_index_id")
        if (last_index_id == ""):
            last_index_id = None

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
        beta = BetaSerieAPI(login, password)
    except BadLoginException as ex:
        logger.error("[BetaBeard] can't log into BetaSeries.com : %s", ex.value['text'])
        sys.exit(0)

    logger.info("[BetaBeard] Login successfull.")
    # ----------- Init SickBeard ----------- #

    sickBeard = SickBeardAPI(sburl, scheme, apikey)

    # ----------- Test SickBeard ----------- #
    if (sickBeard.ping() == False):
        logger.error("[BetaBeard] Can't ping SickBeard on url : %s://%s with apikey = %s",scheme, config.get("SickBeard", "url"), config.get("SickBeard", "apikey"))
        sys.exit(0)
    logger.info("[BetaBeard] Ping SickBeard successfull.")

    # ----------- retrieve last  event processed in betaseries----------- #
    if config.get("BetaBeard", "last_index_id") == "":
        logger.debug("[BetaBeard] last_index_id is None")
        if config.get("BetaBeard", "fullUpdate"):
            shows = beta.show_list();
            logger.debug("[BetaBeard] shows : %s", shows)
            for show in shows:
                logger.info("[BetaBeard] Add show in SickBeard : %s", show)
                success = sickBeard.add_show(show, location, lang, flatten_folder, status, initial, archive)
                if (success == False):
                    logger.error("[BetaBeard] Can't add show %s to sickbeard.", show)


