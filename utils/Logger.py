import sys
from colorama import Fore, Back
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import pathlib
from utils.Settings import Setting as st
Setting = st()

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

SECTION_LEVEL_NUM = 9

class ColorFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        if record.levelno == logging.DEBUG:
            self._style._fmt = Fore.LIGHTBLACK_EX + "%(message)s" + RESET_SEQ
        elif record.levelno == logging.ERROR:
            self._style._fmt = Fore.RED + \
                "%(levelname)s: %(message)s" + RESET_SEQ
        elif record.levelno == logging.CRITICAL:
            self._style._fmt = Back.WHITE + Fore.RED + \
                "%(levelname)s: %(message)s" + RESET_SEQ
        elif record.levelno == logging.WARNING:
            self._style._fmt = Fore.YELLOW + \
                "%(levelname)s: %(message)s" + RESET_SEQ
        elif record.levelno == logging.HEADER:
            self._style._fmt = Fore.LIGHTBLUE_EX + \
                "\n--- %(message)s ---" + RESET_SEQ
        elif record.levelno == logging.COMPLETION:
            self._style._fmt = Fore.GREEN + \
                "\n--- %(message)s ---" + RESET_SEQ
        elif record.levelno == logging.NOTE:
            self._style._fmt = Fore.LIGHTBLUE_EX + \
                "Note: " + RESET_SEQ + "%(message)s" + RESET_SEQ
        else:
            self._style._fmt = "%(message)s"
        return super().format(record)

def combining_filter(record):
    record.location = '%s:%s:%s' % (
        record.module, record.funcName, record.lineno)
    record.locationClickable = '%s:%s' % (record.filename, record.lineno)
    return True

def setup_logging(default_level=Setting.loggingLevel):
    """
    Setup logging configuration
    """
    # triedToCreateFile = False
    # for i in range(0, 2):
    #     try:
    #         if os.path.exists(default_config):
    #             logging.config.fileConfig(default_config, disable_existing_loggers=False)
    #         else:
    #             logging.basicConfig(level=default_level)
    #     except (FileNotFoundError, OSError) as fnfe:
    #         try:
    #             loggingFilePath = pathlib.Path(fnfe.filename).parent
    #             loggingFilePath.mkdir(parents=True, exist_ok=True)
    #         except Exception as e:
    #             pass
    #         if triedToCreateFile:
    #             print(
    #                 f"{Back.WHITE}{Fore.RED}CRITICAL: Cannot find or create the logging directory or file, exiting{Back.RESET}{Fore.RESET}")
    #             raise SystemExit(1)
    #         else:
    #             print(
    #                 f"{Fore.RED}ERROR: Cannot find or create the logging directory or file {loggingFilePath}, creating one..{Fore.RESET}")
    #             triedToCreateFile = True
    #             continue

    # logging level of notes should be just higher than info
    logging.NOTE = 21
    logging.addLevelName(logging.NOTE, "NOTE")

    # logging level of header should be just higher than info
    logging.HEADER = 22
    logging.addLevelName(logging.HEADER, "HEADER")

    # logging level of notes should be just higher than info
    logging.COMPLETION = 31
    logging.addLevelName(logging.COMPLETION, "COMPLETION")

    # Create logger
    logger = logging.getLogger('root')
    logger.setLevel(logging.DEBUG)

    # Create handlers
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(Setting.loggingLevel)

    triedToCreateFile = False
    for i in range(0, 2):
        try:
            file_handler = TimedRotatingFileHandler('logs/latest.log', when="D", interval=1, backupCount=0)
        except (FileNotFoundError, OSError) as fnfe:
            try:
                loggingFilePath = pathlib.Path(fnfe.filename).parent
                loggingFilePath.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                pass
            if triedToCreateFile:
                print(
                    f"{Back.WHITE}{Fore.RED}CRITICAL: Cannot find or create the logging directory or file, exiting{Back.RESET}{Fore.RESET}")
                raise SystemExit(1)
            else:
                print(
                    f"{Fore.RED}ERROR: Cannot find or create the logging directory or file {loggingFilePath}, creating one..{Fore.RESET}")
                triedToCreateFile = True
                continue
    file_handler.setLevel(logging.DEBUG)
    file_handler.addFilter(combining_filter)
    file_handler.namer = lambda name: str.replace(name, "latest.log.", "") + ".log"

    # Create formatter
    formatter_timestampedLogWithName = logging.Formatter('[%(asctime)-15s] %(levelname)-10s : %(message)s (%(locationClickable)s)', datefmt='%Y-%m-%d %H:%M:%S')

    # Set formatter for handlers
    file_handler.setFormatter(formatter_timestampedLogWithName)
    stdout_handler.setFormatter(ColorFormatter("%(message)s"))

    # Add handlers to logger
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    # Set logging level for external libraries (PIL in this case)
    logging.getLogger("PIL").setLevel(logging.ERROR)
