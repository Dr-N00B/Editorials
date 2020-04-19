import logging
import os.path
import sys
from Config import AppConfig
from Editorial import IEditorial
import Const
import argparse


log_level ={
	"DEBUG" 	: logging.DEBUG,
	"INFO" 		: logging.INFO,
	"ERROR" 	: logging.ERROR,
	"CRITICAL"	: logging.CRITICAL,
	"WARNING"	: logging.WARNING
}

def setLogger(logger_info):
	logging.basicConfig(level=log_level[logger_info["level"]],
						format=logger_info["format"],
						datefmt=logger_info["date_format"],
						filename=logger_info["file"],
						filemode='w+')


def readCmdLineArgs():
	my_parser = argparse.ArgumentParser(prog='Editorial')
	my_parser.add_argument('-c', '--config', metavar='FILE', action='store', default="editorial.json", help="User specified Configuration file")
	return my_parser.parse_args()

def main():
	cmdline_args = readCmdLineArgs()
	objAppConfig = AppConfig()
	config_data = objAppConfig.loadConfig(cmdline_args.config)
	config_data["logging"]["file"] = objAppConfig.getAbsFilePath(config_data["logging"]["file"], config_data["path"][Const.LOGGING_DIR])
	setLogger(config_data["logging"])
	logger = logging.getLogger(Const.APP_LOG)
	logger.debug("Started Editorial extraction.")
	for np_type, url in config_data["url"].items():
		objEditorial = IEditorial(Const.FILE,config_data["path"]).createInstance(np_type)
		objEditorial.fetchArticle(np_type, url)
	logger.debug("Completed Editorial extraction.")

if __name__ == "__main__":
	 main()