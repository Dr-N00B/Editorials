import os.path
import json
import logging
import Const
import Util
from datetime import date, datetime,timedelta
from urllib.parse import quote_plus

from pymongo import MongoClient,ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure,BulkWriteError

logger = logging.getLogger(Const.APP_NAME)

class IPersistData:
	def __init__(self):
		pass

	def getInstance(self, persist_type, config_data):
		if persist_type == Const.FILE:
			return PersistDataToFile(config_data)
		elif persist_type == Const.DB:
			return PersistDataToDB(config_data)
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

	def flushData(self):
		pass

	


class PersistDataToFile(IPersistData):
	config_data = None
	def __init__(self,config_data):
		# super.__init__(config_data)
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
				feed_date_dict[key][Const.MAX_FEED_DATE] = Util.convertStrToDate(feed_date_dict[key][Const.MAX_FEED_DATE])
				feed_date_dict[key][Const.MIN_FEED_DATE] = Util.convertStrToDate(feed_date_dict[key][Const.MIN_FEED_DATE])
		return feed_date_dict
	
	def storeMaxFeedDate(self, feed_date_dict):
		feed_date_str = {}
		Util.makeDir(PersistDataToFile.config_data[Const.STORAGE_LOC])
		filename = Util.getAbsPath(PersistDataToFile.config_data[Const.STORAGE_LOC],Const.FEED_DATE_FILE)

		for key in feed_date_dict:
			max_date_str = Util.convertDateToStr(feed_date_dict[key][Const.MAX_FEED_DATE])
			min_date_str = Util.convertDateToStr(feed_date_dict[key][Const.MIN_FEED_DATE])
			feed_date_str[key] = {Const.MAX_FEED_DATE: max_date_str, Const.MIN_FEED_DATE: min_date_str}

		with open(filename, "w",encoding="utf-8") as f:
			f.write(json.dumps(feed_date_str,indent=4))


class PersistDataToDB(IPersistData):
	config_data = None
	article_list = []
	curr_np_name = None
	db_conn_url = Const.URI_PREFIX
	conn_handle = None
	db_handle = None
	collection_handle = None
	total_article_inserted = 0 
	def __init__(self,config_data):
		# super().__init__(config_data)
		self.config_data =config_data
		uri_suffix = ''
		if config_data[Const.USER]:
			self.db_conn_url = self.db_conn_url + quote_plus(config_data[Const.USER])
		if config_data[Const.PASSWORD]:
			self.db_conn_url = self.db_conn_url + ':' +quote_plus(config_data[Const.PASSWORD]) + '@'
			uri_suffix = "/?authSource="
			if Const.AUTHDB in config_data and config_data[Const.AUTHDB]:
				uri_suffix = uri_suffix + config_data[Const.AUTHDB]
			else:
				uri_suffix = uri_suffix + 'admin'
		
		self.db_conn_url = self.db_conn_url + config_data[Const.HOST] + ':' + config_data[Const.PORT] + uri_suffix
		self.conn_handle = MongoClient(self.db_conn_url)

		try:
			self.conn_handle.admin.command('ismaster')
		except ConnectionFailure as e:
			logger.exception(f'Exception : {e}')
			raise
		
		self.db_handle = self.conn_handle[config_data[Const.DBNAME]]
		self.collection_handle = self.db_handle[config_data[Const.COLLECTION]]
		self.collection_handle.create_index([(Const.TITLE, DESCENDING), (Const.NAME, ASCENDING)], name='ARTICE_INDEX', unique=True, background=True)

	# def isConnectedDB(self, handle):
	# 	try:
	# 		handle.admin.command('ismaster')
	# 	except:
	# 		logger.info("DB not connected. Connecting...")
	# 		self.connectDB(handle)
	
	
	# def connectDB(self,handle):
	# 	return MongoClient(self.db_conn_url)

	def storeData(self, np_name, article_data):
		if self.curr_np_name is None:
			self.curr_np_name = np_name
		if len(self.article_list) >= 10 or self.curr_np_name != np_name:
			self.storeToDB(self.collection_handle,self.article_list)
			logger.info("Written data to database")
			self.article_list = []
		self.article_list.append(article_data)
		
	
	def storeToDB(self,collection_handle, article_list):
		try:
			count = collection_handle.insert_many(article_list, ordered=False)
			self.total_article_inserted = self.total_article_inserted + len(count.inserted_ids)
		except BulkWriteError as e:
			self.total_article_inserted = self.total_article_inserted + e.details["nInserted"]
			logger.warn(f"Articles already exists")
	

	def getMaxFeedDate(self):
		feed_date_dict = {}
		feed_date_collection_handle = self.db_handle['feed_date']
		cursor = feed_date_collection_handle.find({},{'_id':False})
		for doc in cursor:
			max_date = Util.convertDatetimeToDate(doc[Const.MAX_FEED_DATE])
			min_date = Util.convertDatetimeToDate(doc[Const.MIN_FEED_DATE])
			feed_date_dict[doc[Const.NAME]] = {Const.MAX_FEED_DATE: max_date, Const.MIN_FEED_DATE: min_date}
		return feed_date_dict
	
	def storeMaxFeedDate(self, feed_date_dict):
		feed_date_str = {}
		feed_date_collection_handle = self.db_handle['feed_date']
		for key, value in feed_date_dict.items():
			max_date = Util.convertDateToDateTime(value[Const.MAX_FEED_DATE])
			min_date = Util.convertDateToDateTime(value[Const.MIN_FEED_DATE])

			try:
				feed_date_collection_handle.update_one({Const.NAME : key},
														{'$set' : {	Const.MAX_FEED_DATE : max_date, 
																	Const.MIN_FEED_DATE : min_date}}, 
														upsert = True)
			except Exception as e:
				logger.exception(f"{e}")
		

		logger.info("Storing feed date")
		
	def flushData(self):
		if len(self.article_list) > 0:
			self.storeToDB(self.collection_handle,self.article_list)
			logger.info("Flushed data to database")
		self.conn_handle.close()
		logger.info("DB Connection closed")
		logger.info(f"Total articles written to DB : {self.total_article_inserted}")