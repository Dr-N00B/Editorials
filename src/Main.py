import logging
import Util
from Editorial import IEditorial
import Const
import argparse
import sys
import Log


def readCmdLineArgs():
	my_parser = argparse.ArgumentParser(prog='Editorial')
	my_parser.add_argument('-c', '--config', metavar='FILE', action='store', default="app_config.json", help="User specified Configuration file")
	return my_parser.parse_args()

def main():
	cmdline_args = readCmdLineArgs()
	config_file = Util.getAbsPath(Util.getParentDir(),Const.CONFIG_DIR,cmdline_args.config)
	config_data = Util.loadJsonFromFile(config_file)
	Log.initLogger(config_data[Const.LOG_LEVEL])
	logger = logging.getLogger()

	logger.info("Started Editorial extraction.")
	url_file_name = Util.getAbsPath(config_data[Const.URL_FILE])
	url_data  = Util.loadJsonFromFile(url_file_name) 
	IEditorial(config_data[Const.STORAGE]).fetchArticle(url_data)
	logger.info("Completed Editorial extraction.")

if __name__ == "__main__":
	sys.exit(main())