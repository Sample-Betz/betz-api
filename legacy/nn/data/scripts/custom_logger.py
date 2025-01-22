import logging

class LogColors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_colors = {
            'DEBUG': LogColors.CYAN,
            'INFO': LogColors.BLUE,
            'WARNING': LogColors.YELLOW,
            'ERROR': LogColors.RED,
            'CRITICAL': LogColors.MAGENTA,
            'FINISHED': LogColors.GREEN 
        }

        color = log_colors.get(record.levelname, LogColors.RESET)
        message = super().format(record)

        return f"{color}{message}{LogColors.RESET}"
    
def get_logger(name: str) -> logging.Logger:
    """ Returns a colored logger """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  

    console_handler = logging.StreamHandler()
    formatter = ColoredFormatter('[%(asctime)s %(levelname)s]: %(message)s', datefmt='%H:%M:%S')
    console_handler.setFormatter(formatter)

    if not logger.handlers: 
        logger.addHandler(console_handler)

    return logger

FINISHED = 25
logging.addLevelName(FINISHED, "FINISHED")

def log_finished(logger: logging.Logger, message: str) -> None:
    """ Logs a finished message """
    logger.log(FINISHED, message)
