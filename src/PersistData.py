import os.path
import json
import logging
import Const
import Util
from datetime import date, datetime,timedelta

logger = logging.getLogger(Const.APP_NAME)

class IPersistData:
	def __init__(self):
		pass

	def getInstance(self, persist_type, config_data):
		if persist_type == Const.FILE:
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
		np_name = np_name.replace(' ', '_')
		path = Util.getAbsPath(PersistDataToFile.config_data[Const.STORAGE_LOC], np_name)
		Util.makeDir(path)
		
		article_sep = ""
		file_name = np_name + "_" + article_data[Const.FEED_DATE].replace("-","_") + ".txt"
		file_name = Util.getAbsPath(path,file_name)
		if os.path.exists(file_name):
			article_sep = 4 * "\n" + 80 * "=" + 4 * "\n"
			with open(file_name, "r", encoding='utf-8') as f:
				if article_data[Const.TITLE] in f.read():
					logger.info(f"Content with title \"{article_data[Const.TITLE]}\" already present")
					return

		with open(file_name, "a",encoding='utf-8') as f:
			f.write(article_sep)
			for k,v in article_data.items():
				f.write(k + " : " + v + "\n")			
	
	def getMaxFeedDate(self):
		feed_date_dict = {}
		Util.makeDir(PersistDataToFile.config_data[Const.STORAGE_LOC])
		filename = Util.getAbsPath(PersistDataToFile.config_data[Const.STORAGE_LOC],Const.FEED_DATE_FILE)
		if os.path.exists(filename):
			with open(filename, "r") as f:
				feed_date_dict = json.load(f)
			
			for key in feed_date_dict:
				feed_date_dict[key][Const.MAX_FEED_DATE] = datetime.strptime(feed_date_dict[key][Const.MAX_FEED_DATE],Const.DD_MM_YYYY).date()
				feed_date_dict[key][Const.MIN_FEED_DATE] = datetime.strptime(feed_date_dict[key][Const.MIN_FEED_DATE],Const.DD_MM_YYYY).date()

		return feed_date_dict
	
	def storeMaxFeedDate(self, feed_date_dict):
		feed_date_str = {}
		Util.makeDir(PersistDataToFile.config_data[Const.STORAGE_LOC])
		filename = Util.getAbsPath(PersistDataToFile.config_data[Const.STORAGE_LOC],Const.FEED_DATE_FILE)

		for key in feed_date_dict:
			
			max_date_str = feed_date_dict[key][Const.MAX_FEED_DATE].strftime(Const.DD_MM_YYYY)
			min_date_str = feed_date_dict[key][Const.MIN_FEED_DATE].strftime(Const.DD_MM_YYYY)
			feed_date_str[key] = {Const.MAX_FEED_DATE: max_date_str, Const.MIN_FEED_DATE: min_date_str}

		with open(filename, "w",encoding="utf-8") as f:
			f.write(json.dumps(feed_date_str,indent=4))

	# def isContentPresent(self, article_data, file_name):
