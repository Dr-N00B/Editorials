import logging
import sys
import Util
from Editorial import IEditorial
import Const
import argparse
import os


LogLevel ={
	"DEBUG" 	: logging.DEBUG,
	"INFO" 		: logging.INFO,
	"ERROR" 	: logging.ERROR,
	"CRITICAL"	: logging.CRITICAL,
	"WARNING"	: logging.WARNING
}

def setLogger(logger_info):
	log_dir = Util.getAbsPath(Util.getParentDir(),Const.LOGGING_DIR)
	Util.makeDir(log_dir)
	log_file_name = Const.APP_NAME + "_" + str(os.getpid()) + Const.LOG_FILE_EXTN
	log_file_name = Util.getAbsPath(log_dir,log_file_name)
	
	log_level = LogLevel["INFO"]
	
	if Const.LOG_LEVEL in logger_info:
		log_level = LogLevel[logger_info[Const.LOG_LEVEL]]

	logging.basicConfig(level=log_level,
						format=Const.MSG_FORMAT,
						datefmt=Const.LOG_DATE_FORMAT,
						filename=log_file_name,
						filemode='w+')


def readCmdLineArgs():
	my_parser = argparse.ArgumentParser(prog='Editorial')
	my_parser.add_argument('-c', '--config', metavar='FILE', action='store', default="app_config.json", help="User specified Configuration file")
	return my_parser.parse_args()

def main():
	cmdline_args = readCmdLineArgs()
	config_file = Util.getAbsPath(Util.getParentDir(),Const.CONFIG_DIR,cmdline_args.config)
	config_data = Util.loadJsonFromFile(config_file)
	setLogger(config_data)
	logger = logging.getLogger(Const.APP_NAME)
	logger.info("Started Editorial extraction.")
	url_file_name = Util.getAbsPath(config_data[Const.URL_FILE])
	url_data  = Util.loadJsonFromFile(url_file_name) 
	IEditorial(config_data[Const.STORAGE]).fetchArticle(url_data)
	logger.info("Completed Editorial extraction.")

if __name__ == "__main__":
	 main()