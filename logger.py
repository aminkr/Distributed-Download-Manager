import sys
import logging
import os
try:
    import colorlog
except ImportError:
    pass


TRACE_LEVELV_NUM = 5
logging.addLevelName(TRACE_LEVELV_NUM, "TRACE")
def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVELV_NUM):
        self._log(TRACE_LEVELV_NUM, message, args, **kws)
logging.Logger.trace = trace


def setup_logging(log_level = 'debug'):
    root = logging.getLogger(__name__)
    if log_level == 'error':
        root.setLevel(logging.ERROR)
    elif log_level == 'info':
        root.setLevel(logging.INFO)
    else:
        root.setLevel(logging.DEBUG)
    format = '[%(asctime)s] %(module)20s(%(lineno)3d) - %(levelname)-4s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if 'colorlog' in sys.modules and os.isatty(2):
        cformat = '%(log_color)s' + format
        f = colorlog.ColoredFormatter(cformat, date_format,
              log_colors = { 'DEBUG'   : 'reset',  'INFO' : 'green',
                             'WARNING' : 'yellow', 'ERROR': 'red',
                             'CRITICAL': 'bold_red' })
    else:
        f = logging.Formatter(format, date_format)
    ch = logging.StreamHandler()
    ch.setFormatter(f)
    root.addHandler(ch)


setup_logging()
logger = logging.getLogger(__name__)
