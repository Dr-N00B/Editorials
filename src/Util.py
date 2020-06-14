import os.path
import sys
import json
import Const
from datetime import date, datetime,timedelta

def getAbsPath(path, *varArgs):
	abs_path = path
	for subdir in varArgs:
		abs_path = os.path.join(os.path.sep, abs_path, subdir)
	os.path.abspath(abs_path)
	return abs_path

def getParentDir(path = __file__):
	return os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(path)), os.pardir))

def makeDir(path, permission = 0o755):
	if not os.path.isdir(path):
		os.makedirs(path, permission, True)

def loadJsonFromFile(file):
	conf_loaded = {}
	with open(file,'r') as infile:
		conf_loaded = json.load(infile)	
	return conf_loaded

def convertDateToStr(date_str, format=Const.DD_MM_YYYY):
	return date_str.strftime(format)
	
def convertStrToDate(date_str, format=Const.DD_MM_YYYY):
	return datetime.strptime(date_str,format).date()

def convertStrToDateToStr(date_str, format, out_format = Const.DD_MM_YYYY):
	tmp_date = convertStrToDate(date_str,format)
	return convertDateToStr(tmp_date,out_format)

def convertDatetimeToDate(date, format = Const.DD_MM_YYYY):
	return datetime.strptime(date.date().strftime(format),format).date()

def convertDateToDateTime(date):
	return datetime(date.year, date.month, date.day)