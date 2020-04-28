from datetime import datetime


class Logger:
    def __init__(self, log_filename):
        self.file_name = log_filename
        with open(log_filename, 'a+') as log:
            log.write("[%s] Logging initialized.\n" % datetime.utcnow())

    def get_logger(self):
        return self

    def log_info(self, message):
        with open(self.file_name, 'a+') as log:
            log.write("[%s] %s\n" % (datetime.utcnow(), message))


