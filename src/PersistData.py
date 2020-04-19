import os.path
import json
from enum import Enum
import logging
from Config import AppConfig
import Const

logger = logging.getLogger(Const.APP_LOG)

class IPersistData:
	def __init__(self):
		pass

	def getInstance(self, persist_type, config_data):
		if persist_type is Const.FILE:
			return PersistDataToFile(config_data)
		else:
			logger.error(f"Object for storing value in {persist_type}")
			raise NotImplementedError

	def storeData(self,content):
		logger.error(f"Overloaded function not implemented")
		raise NotImplementedError

	def getMaxFeedDate(self):
		logger.error(f"Overloaded function not implemented")
		raise NotImplementedError

	def storeMaxFeedDate(self,np_name, feed_date):
		logger.error(f"Overloaded function not implemented")
		raise NotImplementedError



class PersistDataToFile(IPersistData):
	config_data = None
	def __init__(self,config_data):
		if PersistDataToFile.config_data is None:
			PersistDataToFile.config_data = config_data

	def storeData(self, np_name, article_data):
		path = os.path.join(os.path.sep,PersistDataToFile.config_data[Const.DATA_DIR], np_name)
		# path = AppConfig.getAbsFilePath(np_name, os.path.sep,PersistDataToFile.config_data[Const.DATA_DIR])
		self.makePath(path)
		
		for key in article_data:
			add_space = ""
			file_name = self.getFileName(path,np_name,article_data[key][Const.FEED_DATE])
			if os.path.exists(file_name):
				add_space = 4 * "\n" + 80 * "=" + 4 * "\n"
			
			with open(file_name, "a",encoding='utf-8') as f:
				f.write(add_space)
				f.write(Const.NAME + ":" + article_data[key][Const.NAME] + "\n")
				f.write(Const.TITLE + ":" + article_data[key][Const.TITLE]+ "\n")
				f.write(Const.FEED_DATE + ":" + article_data[key][Const.FEED_DATE]+ "\n")
				f.write(Const.DATE + ":" + article_data[key][Const.DATE]+ "\n")
				f.write(Const.URL + ":" + article_data[key][Const.URL]+ "\n")
				f.write(Const.DESCRIPTION + ":" + article_data[key][Const.DESCRIPTION]+ "\n")
				f.write(Const.DATA + ":" + article_data[key][Const.DATA]+ "\n")			

	def getFileName(self, path,np_name, feed_date):
		file_name_only = np_name + "_" + feed_date.replace("-","_") + Const.DATA_FILE_EXTN
		abs_file_name = os.path.join(os.path.sep, path, file_name_only)
		return abs_file_name


	def makePath(self,path):
		if not os.path.isdir(path):
			os.makedirs(path, 0o755, True)
	
	def getMaxFeedDate(self):
		max_feed_date_dict = {}
		filename = AppConfig().getAbsFilePath(Const.FEED_DATE_FILE, PersistDataToFile.config_data[Const.DATA_DIR])
		if os.path.exists(filename):
			with open(filename, "r") as f:
				max_feed_date_dict = json.load(f)
		return max_feed_date_dict
	
	def storeMaxFeedDate(self, np_name, feed_date):
		filename = AppConfig().getAbsFilePath(Const.FEED_DATE_FILE, PersistDataToFile.config_data[Const.DATA_DIR])
		data = {}
		if os.path.exists(filename):
			with open(filename, "r",encoding="utf-8") as f:
				data  = json.load(f)
		
		data[np_name] = feed_date
		with open(filename, "w",encoding="utf-8") as f:
			f.write(json.dumps(data))
