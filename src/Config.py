import os.path
from enum import Enum
import json
import Const

class AppConfig:
	conf_loaded = {}
	def __init__(self):
		pass

	def loadConfig(self,conf_file):
		path_formed = {}

		if conf_file in self.conf_loaded:
			return self.conf_loaded[conf_file]

		for dir in [Const.CONFIG_DIR, Const.LOGGING_DIR, Const.DATA_DIR]:
			path_formed[dir] = self.getAbsPath(dir)
		
		
		abs_config_file = self.getAbsFilePath(conf_file, Const.CONFIG_DIR)

		with open(abs_config_file,'r') as infile:
			self.conf_loaded = json.load(infile)
		self.conf_loaded["path"] = path_formed
		return self.conf_loaded
	
	def getAbsFilePath(self, filename, subdir):
		abs_path = self.getAbsPath(subdir)
		return os.path.join(os.path.sep,abs_path,filename)
	
	def getAbsPath(self, subdir):
		return os.path.abspath(os.path.join(self.getParentDir(), subdir))
	
	def getParentDir(self):
		return os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)