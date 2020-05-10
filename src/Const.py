# This file has all the constants defined to be used in all other files

# constants related to article
NAME			= 'name'
TITLE 			= 'title'
DESCRIPTION		= 'description'
DATE 			= 'date'
FEED_DATE		= 'pubDate'
DATA 			= 'story'
URL 			= 'link'

# location to store articles
FILE			= 'file'
DB				= 'db'

# Date formats of rss
DD_MM_YYYY		= '%d-%m-%Y'

# parser types
HTML_PARSER		= 'html.parser'
XML_PARSER		= 'lxml-xml'

# default path related constants
CONFIG_DIR		= "config"
LOGGING_DIR		= "log"
DATA_DIR		= "data"
SRC_DIR			= "src"

# file related changes
FEED_DATE_FILE	= "max_feed_date.json"
MAX_FEED_DATE	= "max_date" 
MIN_FEED_DATE	= "min_date" 

#Logger & log file Name
APP_NAME		= 'Editorial'
LOG_FILE_EXTN	= '.log'

# Config file related constants
URL_FILE		= "url_file"
STORAGE			= "storage"	
STORAGE_TYPE	= "type"
STORAGE_LOC		= "path"
MSG_FORMAT		= "%(asctime)s : %(levelname)s : %(module)s : %(funcName)s: %(message)s"
LOG_LEVEL		= "log_level"
LOG_DATE_FORMAT	= "%d-%m-%Y %H:%M:%S"


#url file related constants
RSS_URL			= "url"
RSS				= "rss"
PAGE			= "page"
PUBDATE_FORMAT	= "date_format"
DATE_FORMAT		= "format"
CHILD_INC		= "child_include"
CHILD_EXC		= "child_exclude"
ARRTIBS			= "attribute"
RSS_TAGS		= "tags"
TAG				= "tag"

# dump stats
TOTAL_URL		= "url_count"
SKIPPED_URL		= "url_skipped"
PROCESSED_URL	= "url_processed"

# these words needs to be replaced with their coresponding values in data
TYPESETTING_ENTITES  = {
	"&#162;"	:	"¢",
	"&#163;"	:	"£", 
	"&#167;"	:	"§",
	"&#169;"	:	"(c)",
	"&#171;"	:	"«",
	"&#187;"	:	"»",
	"&#174;"	:	"(R)",
	"&#176;"	:	"°",
	"&#177;"	:	"+/-",
	"&#182;"	:	"¶",
	"&#183;"	:	"·",
	"&#188;"	:	"1/2",
	"&#8211;"	:	"–",
	"&#8212;"	:	"—",
	"&#8216;" 	:	"'",
	"&#8217;" 	:	"'",
	"&#39;" 	:	"'",
	"&#8218;"	:	"‚",
	"&#8220;"	:	"\"",
	"&#8221;"	:	"\"",
	"&#8222;"	:	"„",
	"&#8224;" 	:	"*",
	"&#8225;" 	:	"**",
	"&#8226;"	:	"•",
	"&#8230;"	:	"…",
	"&#8242;" 	:	"'",
	"&#8243;" 	:	"\"",
	"&#8364;"	:	"€",
	"&#8482;"	:	"™",
	"&#8776;"	:	"≈",
	"&#8800;"	:	"≠",
	"&#8804;" 	:	"<=",
	"&#8805;" 	:	">=",
	"&#062;"	:	"<",
	"&#060;"	:	">",

	"&cent;"  	:  "¢",	
	"&pound;"	:  "£", 	
	"&sect;"	:  "§",	
	"&copy;"	:  "(c)",	
	"&laquo;" 	:  "«",	
	"&raquo;"	:  "»",	
	"&reg;"		:  "(R)",	
	"&deg;"		:  "°",	
	"&plusmn;"	:  "+/-",	
	"&para;"	:  "¶",	
	"&middot;"	:  "·",	
	"&frac12;"	:  "1/2",	
	"&ndash;"	:  "–",	
	"&mdash;"	:  "—",	
	"&lsquo;" 	:  "'",	
	"&rsquo;"	:  "'",	
	"&sbquo;"	:  "‚",	
	"&ldquo;" 	:  "\"",	
	"&rdquo;"	:  "\"",	
	"&bdquo;"	:  "„",	
	"&dagger;"	:  "*",	
	"&Dagger;"	:  "**",	
	"&bull;"	:  "•",	
	"&hellip;"	:  "…",	
	"&prime;" 	:  "'",	
	"&Prime;"	:  "\"",	
	"&euro;"	:  "€",	
	"&trade;"	:  "™",	
	"&asymp;"	:  "≈",	
	"&ne;"		:  "≠",	
	"&le;" 		:  "<=",	
	"&ge;"		:  ">=",	
	"&lt;" 		:  "<",	
	"&gt;"		:  ">",
	"&nbsp;"	:  " ",
	"&amp;"		:  "&"
}