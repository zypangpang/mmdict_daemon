from constants import DEBUG
import logging.config

log_file="./mmdict.log"
logging_config={
    'version': 1,
    'formatters':{
        'default':{
            'format':'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers':{
        'console':{
            'level':"INFO",
            'class':"logging.StreamHandler",
            'formatter':"default"
        },
        'file':{
            "level":"INFO",
            "class":"logging.handlers.TimedRotatingFileHandler",
            'formatter':"default",
            "filename": log_file,
            "when":"D",
            "backupCount":3
        }
    },
    'root':{
        "level":"INFO",
        "handlers":['console'] if DEBUG else ['console','file']
    }
}

logging.config.dictConfig(logging_config)

