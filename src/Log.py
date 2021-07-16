import logging
import logging.config
import os
import Util

APP_NAME        = "Editorial"
LOGGING_DIR		= "log"

log_dict = {
    'version':1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s : [%(levelname)s]  : %(funcName)s: %(message)s'
        },
    },
    'handlers': {
        'file_handler': {
            'level': 'INFO',
            'filename': '{log_path}/{prefix}_{pid}.log',
            'class': 'logging.FileHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file_handler'],
            'propagate': 1,
            'level':'INFO'
        },
    }
}


def initLogger(custom_level=None, app_name=APP_NAME):
    log_dir = Util.getAbsPath(Util.getParentDir(),LOGGING_DIR)
    log_file = log_dict['handlers']['file_handler']['filename']
    file =log_file.format(log_path=log_dir,prefix=app_name,pid=str(os.getpid()))
    log_dict['handlers']['file_handler']['filename'] = Util.getAbsPath(log_dir,file)
    
    if custom_level:
        custom_level = custom_level.upper()
        log_dict['handlers']['file_handler']['level']=custom_level
        log_dict['loggers']['']['level']=custom_level
    
    logging.config.dictConfig(log_dict)
