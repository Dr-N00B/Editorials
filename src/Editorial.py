import requests
import re
from bs4 import BeautifulSoup as bs,NavigableString,CData
import urllib3
from datetime import date, datetime,timedelta
from PersistData import IPersistData
import logging
import Const

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(Const.APP_NAME)
	

class IEditorial:
	max_feed_dict = {}
	stats = {}
	objStorage = None
	def __init__(self,config):
		if IEditorial.objStorage is None:
			IEditorial.objStorage = IPersistData().getInstance(config[Const.STORAGE_TYPE], config)
			IEditorial.max_feed_dict = IEditorial.objStorage.getMaxFeedDate()

	def fetchArticle(self,config_data):
		for np_title, title_info in config_data.items():
			rss_url = title_info[Const.RSS_URL]
			rss_parsed_data = self.parseRssPage(np_title,rss_url,title_info[Const.RSS][Const.RSS_TAGS],title_info[Const.RSS][Const.PUBDATE_FORMAT])
			for link in rss_parsed_data:
				html_page = bs(self.downloadPage(link), Const.HTML_PARSER)
				paged_data = self.parsePageData(html_page,title_info[Const.PAGE])
				rss_parsed_data[link].update(paged_data)
				IEditorial.objStorage.storeData(np_title,rss_parsed_data[link])

		IEditorial.objStorage.storeMaxFeedDate(self.max_feed_dict)
		self.dumpStats(self.stats)

	def parsePageData(self, html_page,config_page):
		data_dict = {}
		for p_tag_name, tag_info in config_page.items():
			tag_name  = tag_info[Const.TAG]
			attrib = {}
			child_exl = []
			child_inc = []
			tag_content = None
			if "partial_attribute" in tag_info:
				attrib_id = tag_info["partial_attribute"]["name"]
				regex = tag_info["partial_attribute"]["value"]
				pattern = "<"+ tag_name +".*?"+ attrib_id + ".*(" + regex + "?\")"
				attrib_val = re.search(str(pattern), str(html_page)).group(1).rstrip("\"")
				attrib[attrib_id] = attrib_val

			elif Const.ARRTIBS in tag_info:
				attrib = tag_info[Const.ARRTIBS]
				
			tag_content = html_page.body.find_all(tag_name, attrs=attrib)

			if Const.CHILD_INC in tag_info:
				child_inc = tag_info[Const.CHILD_INC]	
				if Const.CHILD_EXC in tag_info:
					child_exl = tag_info[Const.CHILD_EXC]
				
			tag_content = self.processData(tag_content,child_inc, child_exl)

			if p_tag_name == Const.DATE:
				tag_content = self.processDate(tag_content, tag_info[Const.DATE_FORMAT])

			data_dict[p_tag_name] = tag_content
		return data_dict
			

	def downloadPage(self,url):
		try:
			logger.debug(f"Downloading url for parsing : {url}")
			resp = requests.get(url=url, verify=False)
		except requests.exceptions.Timeout as eto:
			logger.warning(f"Request timed out for url : {url}.")
			logger.exception(f"Exception happened : {eto}")
		except requests.exceptions.RequestException as e:
			logger.exception(f"Exception happened : {e}")
		resp.encoding = 'utf-8'
		logger.debug("Page downloading completed.")
		return resp.text

	def parseRssPage(self,np_title,feed_url, list_tags_to_process,pub_date_format):
		char_to_strip = '?\n\r\t '
		logger.info(f"RSS page parsing started for {np_title}")
		parsed_rss = {}
		
		# download the rss default page to parse the article related information  
		page = self.downloadPage(feed_url)

		# parse the html page's tree using default parser
		soup = bs(page, Const.XML_PARSER)
		logger.info("BS4 Page parsing and tree creation done.")

		# convert np_title to title case outside loop to avoid processing every time
		np_title = np_title.replace('_', ' ').title()

		self.stats[np_title] = {}
		# every article is in <item> tag which is a child of the <channel> tag.
		channel_tag = soup.channel
		url_all = 0
		url_skipped = 0
		for item in channel_tag.find_all('item'):
			item_dict = {}
			url_all = url_all + 1
			item_dict[Const.NAME] = np_title
			# Mandatory arguments to process are:
			#	title, link and pubDate.
			item_dict[Const.TITLE] = self.cleanCDATA(item.title.get_text().strip(char_to_strip))
			
			item_dict[Const.FEED_DATE] = self.cleanCDATA(item.pubDate.get_text().strip(char_to_strip))
			item_dict[Const.FEED_DATE] = self.processDate(item_dict[Const.FEED_DATE],pub_date_format)
			
			if self.isArticleProcessed(np_title,item_dict[Const.FEED_DATE]):
				logger.debug(f"URL {item_dict[Const.TITLE]} already processed. Skipping...")
				url_skipped = url_skipped + 1
				continue
			
			
			item_dict[Const.URL] = self.cleanCDATA(item.link.get_text().strip(char_to_strip))

			for tag in list_tags_to_process:
				item_dict[tag] = self.cleanCDATA(item.find(tag).get_text().strip(char_to_strip))
			parsed_rss[item_dict[Const.URL]] = item_dict
		
		logger.debug("RSS page parsing completed.")
		self.stats[np_title] = {Const.TOTAL_URL : url_all, Const.PROCESSED_URL : url_all - url_skipped, Const.SKIPPED_URL: url_skipped}
		return parsed_rss
	
	def processDate(self,date_str, date_format, str_out_date_format=Const.DD_MM_YYYY):
		date_arr = date_str.split(' ')
		date_str_processed = ""	
		if date_arr[0].find(',') != -1 or date_arr[0].find(':') != -1 :
			date_str_processed = " ".join([date_arr[1], date_arr[2], date_arr[3]])
		else:
			date_str_processed = " ".join([date_arr[0],date_arr[1], date_arr[2]])
		date_str_processed = date_str_processed.replace(',','')
		date_str_processed = datetime.strptime(date_str_processed,date_format).date().strftime(str_out_date_format)
		return date_str_processed
	
	def processData(self, content, subtag_to_include_list, subtag_to_exclude_list=[]):
		data = ""
		for data_tag in content:
			for child in data_tag.children:
				if child.name in subtag_to_include_list:
					for exclude_tag in subtag_to_exclude_list:
						for exclude_tag in child.find_all(exclude_tag): 
							exclude_tag.decompose()
					data = data + child.get_text().strip()

		if len(data) == 0:
			return data_tag.get_text().strip()
		return data

	def cleanCDATA(self, content):
		tag_pattern =  r"<.*?>"
		content =  re.sub(tag_pattern, '', content)

		# replace special typesetting characters
		speacial_char_pattern = r"&.*?;"
		special_char_list = re.findall(speacial_char_pattern,content)

		for special_char in special_char_list:
			content = re.sub(special_char, Const.TYPESETTING_ENTITES[special_char], content)
		return content

	def isArticleProcessed(self,np_title,feed_date_str):
		feed_date = datetime.strptime(feed_date_str,Const.DD_MM_YYYY).date()
		
		# if dictionary already has entry for the np_type
		if np_title in 	self.max_feed_dict:
			max_date = self.max_feed_dict[np_title][Const.MAX_FEED_DATE]
			min_date = self.max_feed_dict[np_title][Const.MIN_FEED_DATE]
			
			# if date is less than min date processed
			if feed_date <= min_date:
				self.max_feed_dict[np_title][Const.MIN_FEED_DATE] = feed_date
				return False
			elif feed_date >= max_date:
				self.max_feed_dict[np_title][Const.MAX_FEED_DATE] = feed_date
				return False
			else:
				return True
		
		else:
			self.max_feed_dict[np_title] = {Const.MAX_FEED_DATE : feed_date, Const.MIN_FEED_DATE : feed_date}
		return False

	def dumpStats(self,stats_dict):
		total_url = 0
		processed_url = 0
		skipped_url = 0 
		logger.info(f"================ Begin : Stats==============")
		for key, value in stats_dict.items():
			logger.info(f"'{key}' Stats.")
			logger.info(f"{Const.TOTAL_URL} : {value[Const.TOTAL_URL]}.")
			logger.info(f"{Const.PROCESSED_URL} : {value[Const.PROCESSED_URL]}.")
			logger.info(f"{Const.SKIPPED_URL} : {value[Const.SKIPPED_URL]}.")
			total_url = total_url + int(value[Const.TOTAL_URL])
			processed_url = processed_url + int(value[Const.PROCESSED_URL])
			skipped_url = skipped_url + int(value[Const.SKIPPED_URL])
		
		logger.info(f"TOTAL URLS FOUND : {total_url}")
		logger.info(f"TOTAL URL PROCESSED : {processed_url}")
		logger.info(f"TOTAL URLS SKIPPED : {skipped_url}")

		logger.info(f"================ End : Stats ================")

			
			