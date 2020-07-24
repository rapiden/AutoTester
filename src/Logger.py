import logging

# Code largely based on snippet by StackOverflow user eos87.

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


class Logger:
    def __init__(self, log_name, log_file, level=logging.INFO):
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)

        logger = logging.getLogger(log_name)
        logger.setLevel(level)
        logger.addHandler(handler)

        self.log_name = log_name
        self.handler = handler
        self.logger = logger

    def log_info(self, message, log_to_console=False):
        self.logger.info(message)
        if log_to_console is True:
            self.__log_to_console(f'INFO: {message}')

    def log_error(self, message, log_to_console=False):
        self.logger.error(message)
        if log_to_console is True:
            self.__log_to_console(f'ERROR: {message}')

    def __log_to_console(self, message):
        print(f'[{self.log_name}] {message}')

    def __del__(self):
        handlers = self.logger.handlers
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
