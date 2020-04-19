import requests
import re
import os.path
from bs4 import BeautifulSoup as bs,NavigableString,CData
import urllib3
from datetime import date, datetime,timedelta
from PersistData import IPersistData
import logging
import Const

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(Const.APP_LOG)
	
	
class IEditorial:
	max_feed_dict = None
	objStorage = None
	def __init__(self, storage_type,config_data):
		if IEditorial.objStorage is None:
			IEditorial.objStorage = IPersistData().getInstance(storage_type,config_data)
			IEditorial.max_feed_dict = IEditorial.objStorage.getMaxFeedDate()

	def createInstance(self,url_type):
		objEditorial = None
		if url_type.upper() == "THE_HINDU":
			objEditorial = TheHindu()
		elif url_type.upper() == "THE_INDIAN_EXPRESS":
			objEditorial = TheIndianExpress()
		elif url_type.upper() == "THE_TIMES_OF_INDIA":
			objEditorial = TheTimesOfIndia()
		elif url_type.upper() == "THE_NEW_INDIAN_EXPRESS":
			objEditorial = TheNewIndianExpress()
		else:
			raise NotImplementedError
		logger.info(f"Successfully created object of type {type(objEditorial)}")
		return objEditorial

	def fetchArticle(self,np_title,rss_url):
		raise NotImplementedError

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

	def parseRssPage(self,np_title,feed_url, *var_TagsToProcess):
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

		# every article is in <item> tag which is a child of the <channel> tag.
		channel_tag = soup.channel
		for item in channel_tag.find_all('item'):
			item_dict = {}
			# Mandatory arguments to process are:
			#	title, link and pubDate.
			item_dict[Const.NAME] = np_title
			item_dict[Const.TITLE] = item.title.get_text().strip(char_to_strip)
			item_dict[Const.FEED_DATE] = item.pubDate.get_text().strip(char_to_strip)
			item_dict[Const.URL] = item.link.get_text().strip(char_to_strip)

			for tag in var_TagsToProcess:
				item_dict[tag] = item.find(tag).get_text().strip(char_to_strip)
			parsed_rss[item_dict[Const.URL]] = item_dict
		logger.debug("RSS page parsing completed.")
		return parsed_rss
	
	def processDate(self,date_str, date_format, str_out_date_format=Const.DD_MM_YYYY):
		date_arr = date_str.split(' ')
		date_str_processed = ""
		if date_arr[0].find(',') != -1 :
			date_str_processed = "-".join([date_arr[1], date_arr[2], date_arr[3]])
		else:
			date_str_processed = "-".join([date_arr[0],date_arr[1], date_arr[2]])
		date_str_processed = date_str_processed.replace(',','')
		date_str_processed = datetime.strptime(date_str_processed,date_format).date().strftime(str_out_date_format)
		return date_str_processed
	
	def processData(self, data_tag, subtag_to_include_list, subtag_to_exclude_list=[]):
		data = ""
		for child in data_tag.children:
			if child.name in subtag_to_include_list:
				for exclude_tag in subtag_to_exclude_list:
					for exclude_tag in child.find_all(exclude_tag): 
						exclude_tag.decompose()
				data = data + child.get_text().strip()

		return data

	def isArticleAlreadyProcessed(self, np_title, feed_date):
		if np_title in IEditorial.max_feed_dict:
			feed_date_date = datetime.strptime(feed_date,Const.DD_MM_YYYY).date()
			max_feed_date = datetime.strptime(IEditorial.max_feed_dict[np_title],Const.DD_MM_YYYY).date()
			if(feed_date_date <= max_feed_date):
				return True
		return False
	
	def extractMaxFeedDate(self, article_info):
		max_feed_date = None
		for key,value in article_info.items():
			curr_date = datetime.strptime(value[Const.FEED_DATE], Const.DD_MM_YYYY).date()
			if max_feed_date is None:
				max_feed_date = curr_date
			
			if curr_date > max_feed_date :
				max_feed_date = curr_date
		
		return max_feed_date

class TheHindu(IEditorial):
	def __init__(self):
		pass

	def fetchArticle(self,np_title,rss_url):
		article_info = {}
		logger.info(f"Article fetching started for : {np_title}")
		
		parsed_rss_feed_dict = self.parseRssPage(np_title, rss_url, Const.DESCRIPTION)

		for link in parsed_rss_feed_dict :
			paresed_rss_link = parsed_rss_feed_dict[link]
			
			# original feed date captured is in the format : Fri, 17 Apr 2020 01:06:53 +0530
			paresed_rss_link[Const.FEED_DATE] = self.processDate(paresed_rss_link[Const.FEED_DATE],Const.DD_MON_YYYY)

			if self.isArticleAlreadyProcessed(np_title, paresed_rss_link[Const.FEED_DATE]):
				logger.debug(f"Article {paresed_rss_link[Const.TITLE]} already stored. Skipping...")
				continue

			logger.debug(f"Downloading the page and creating parse tree for : {link}")
			html_page = bs(self.downloadPage(link), Const.HTML_PARSER)

			# get the article date from the article page
			date = html_page.body.find("span", attrs={"class":"blue-color ksl-time-stamp"}).get_text().strip()
			paresed_rss_link[Const.DATE] = self.processDate(date,Const.MONTH_DD_YYYY)

			data_tag =  html_page.body.find(id=self.has_attr)
			paresed_rss_link[Const.DATA] = self.processData(data_tag, ['p'])
			
			article_info[paresed_rss_link[Const.TITLE]] = paresed_rss_link
			
		logger.info(f"Articles fetched for news paper : {np_title}")
	
		IEditorial.objStorage.storeData(np_title,article_info)
		curr_max_date = self.extractMaxFeedDate(article_info)
		if curr_max_date is not None:
			curr_max_date = curr_max_date.strftime(Const.DD_MM_YYYY)
			IEditorial.objStorage.storeMaxFeedDate(np_title, curr_max_date)
	
	def has_attr(self,id):
		return id and re.compile("content-body-.*").search(id)
	
	
class TheIndianExpress(IEditorial):
	def __init__(self):
		pass
	
	def fetchArticle(self,np_title,rss_url):
		article_info = {}
		logger.info(f"Article fetching started for : {np_title}")
		
		parsed_rss_feed_dict = self.parseRssPage(np_title, rss_url)

		for link in parsed_rss_feed_dict :
			paresed_rss_link = parsed_rss_feed_dict[link]
			
			# original feed date captured is in the format : Fri, 17 Apr 2020 01:06:53 +0530
			paresed_rss_link[Const.FEED_DATE] = self.processDate(paresed_rss_link[Const.FEED_DATE],Const.DD_MON_YYYY)

			if self.isArticleAlreadyProcessed(np_title, paresed_rss_link[Const.FEED_DATE]):
				logger.debug(f"Article {paresed_rss_link[Const.TITLE]} already stored. Skipping...")
				continue
			
			logger.debug(f"Downloading the page and creating parse tree for : {link}")
			html_page = bs(self.downloadPage(link), Const.HTML_PARSER)

			paresed_rss_link[Const.DESCRIPTION] = html_page.body.find("h2", attrs={"itemprop" :"description","class":"synopsis"}).get_text()
			date = html_page.body.find("span", attrs={"itemprop" :"dateModified"}).get_text().split(':',1)[1].strip()
			
			paresed_rss_link[Const.DATE] = self.processDate(date,Const.MONTH_DD_YYYY)
			
			# get data.
			article = html_page.body.find("div", attrs={"itemprop" :"articleBody","class":"full-details"}).extract()

			paresed_rss_link[Const.DATA] = self.processData(article,['p'])

			article_info[paresed_rss_link[Const.TITLE]] = paresed_rss_link
			

		logger.info(f"Articles fetched for news paper : {np_title}")

		IEditorial.objStorage.storeData(np_title,article_info)
		curr_max_date = self.extractMaxFeedDate(article_info)
		if curr_max_date is not None:
			curr_max_date = curr_max_date.strftime(Const.DD_MM_YYYY)
			IEditorial.objStorage.storeMaxFeedDate(np_title, curr_max_date)
		# IEditorial.objStorage.storeMaxFeedDate(np_title, self.extractMaxFeedDate(article_info))
		return

class TheTimesOfIndia(IEditorial):
	def __init__(self):
		pass

	def fetchArticle(self,np_title,rss_url):
		article_info = {}
		logger.info(f"Article fetching started for : {np_title}")
		
		parsed_rss_feed_dict = self.parseRssPage(np_title, rss_url,Const.DESCRIPTION)
		for link in parsed_rss_feed_dict :
			paresed_rss_link = parsed_rss_feed_dict[link]
			# original feed date captured is in the format : Fri, 17 Apr 2020 19:53:00 IST
			paresed_rss_link[Const.FEED_DATE] = self.processDate(paresed_rss_link[Const.FEED_DATE],Const.DD_MON_YYYY)

			if self.isArticleAlreadyProcessed(np_title, paresed_rss_link[Const.FEED_DATE]):
				logger.debug(f"Article {paresed_rss_link[Const.TITLE]} already stored. Skipping...")
				continue

			logger.debug(f"Downloading the page and creating parse tree for : {link}")
			
			html_page = bs(self.downloadPage(link), Const.HTML_PARSER)

			# article date. format is : "July 31, 2014,". last comma is also there
			date = html_page.body.find("span", attrs={"class":"date"}).get_text()
			paresed_rss_link[Const.DATE] = self.processDate(date,Const.MONTH_DD_YYYY)
			
			# data processing
			data = html_page.body.find("div", attrs={"class" :"content"})


			# remove tags from content
			paresed_rss_link[Const.DATA] = self.processData(data, ['p'])

			article_info[paresed_rss_link[Const.TITLE]] = paresed_rss_link
			
		logger.info(f"Articles fetched for news paper : {np_title}")
		
		IEditorial.objStorage.storeData(np_title,article_info)
		curr_max_date = self.extractMaxFeedDate(article_info)
		if curr_max_date is not None:
			curr_max_date = curr_max_date.strftime(Const.DD_MM_YYYY)
			IEditorial.objStorage.storeMaxFeedDate(np_title, curr_max_date)
		return

class TheNewIndianExpress(IEditorial):
	def __init__(self):
		pass

	def fetchArticle(self,np_title,rss_url):
		article_info = {}
		logger.info(f"Article fetching started for : {np_title}")
		
		parsed_rss_feed_dict = self.parseRssPage(np_title, rss_url,Const.DESCRIPTION, Const.DATA)

		for link in parsed_rss_feed_dict :
			paresed_rss_link = parsed_rss_feed_dict[link]
			
			# original feed date captured is in the format : Friday, April 17, 2020 07:39 AM +0530
			paresed_rss_link[Const.FEED_DATE] = self.processDate(paresed_rss_link[Const.FEED_DATE],Const.MONTH_DD_YYYY)

			if self.isArticleAlreadyProcessed(np_title, paresed_rss_link[Const.FEED_DATE]):
				logger.debug(f"Article :- {paresed_rss_link[Const.TITLE]} already stored. Skipping...")
				continue
			
			# here both dates are same
			paresed_rss_link[Const.DATE] = paresed_rss_link[Const.FEED_DATE]
			# remove tags from content
			paresed_rss_link[Const.DATA] = re.sub(r'<.*?>','', paresed_rss_link[Const.DATA])

			article_info[paresed_rss_link[Const.TITLE]] = paresed_rss_link
				
		logger.info(f"Articles fetched for news paper : {np_title}")

		IEditorial.objStorage.storeData(np_title,article_info)
		curr_max_date = self.extractMaxFeedDate(article_info)
		if curr_max_date is not None:
			curr_max_date = curr_max_date.strftime(Const.DD_MM_YYYY)
			IEditorial.objStorage.storeMaxFeedDate(np_title, curr_max_date)
		return