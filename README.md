# Editorials
	Extract Editorials from newspapers using the RSS feed provided by newspapers. Simply provide the tags which needs to be processed in a config file named "action_items.json". 

## Config file
	Config file is a JSON file. Either pass using command line or use default file present in /config path.
	Config parameters are:
	url_file : [path to the file where action item file is present]
	log_level : INFO|DEBUG|WARN or ERROR
	storage : storage location where the extracted articles will be stored.
				for now only file is supported.
	
	{
		"url_file"  : "D:\\Projects\\python\\Editorials\\config\\action_items.json",
		"log_level": "DEBUG",
		"storage" : {
			"type" : "file",
			"path" : "D:\\Projects\\python\\Editorials\\data"
		}
	}
	`