# Editorials
Extract Editorials from newspapers using the RSS feed provided by newspapers. Simply provide the tags which 
needs to be processed in a config file named "action_items.json". 

## Config file
Config file is a JSON file. Either pass using command line or use default file present in /config path. 

Config parameters are:

```JSON
"url_file"  : "path to the file where all tags related information is present",	"log_level":  "log level in python. Different log levels are DEBUG, INFO, WARNING, ERROR, CRITICAL",
"storage" : {
	"type" 		: "file or db, only one at a time",
	"path" 		: "path only applicable for file only",
	"host" 		: "hostname/ip address",
	"port" 		: "port number",
	"username" 	: "username, if username and password not given, it will try to connect without credential",
	"password" 	: "password, plaintext as of now",
	"database"	: "db name",
	"collection" 	: "collection name",
	"authdb"	: "authentication db, optional, default 'admin' will be used"
}
```

## Action file
This file is a json file which will have all the information about the tags to process and the attributes of a tag
to uniquely identify that tag. Action file will have below format.

```JSON



"Newspaper title" : 
{	
	"url" : "url to the rss feed",
	"rss" : {
		"tags":["list of comma separated tags to process at rss page for each article"],
		"date_format" : "date format. Only month date and year format is to be supplied."
	},
	"page" : {
		"item" : {
			"tag" : "tag_name", 
			"attribute" : { "atttibute name" : "value" },
			"child_include" : ["comma separated tags to include within this tag to extract the content"],
			"child_exclude" : ["comma separated tags to exclude within this tag to extract the content"],
			"format" : "date format if the field is a date."
 		}
	}
}
```

All keys are compulsory except "child_include" , "child_exclude". and "format" has to be given if only the item is of type date.

.e.g
```JSON
"The New York Time" : 
 {	
	"url" : "http://www.nytimes.com/svc/collections/v1/publish/www.nytimes.com/column/charles-m-blow/rss.xml",
	"rss" : {
		"tags":["description"],
		"date_format" : "%d %b %Y"
	},
	"page" : {
		"date" : {
			"tag" : "time", 
			"attribute" : {},
			"child_include" : ["none"],
			"format" : "%B %d %Y"
 		},
		"story" : {
			"tag" : "div",
			"attribute" : {"class":"css-53u6y8"},
			"child_include" : ["p"]
		}
	}
}
```
