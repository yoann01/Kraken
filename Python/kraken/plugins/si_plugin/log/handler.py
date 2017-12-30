import logging

from kraken.plugins.si_plugin.utils import *

logging.INFORM = 25


class DCCHandler(logging.Handler):
    """Logging Handler for Softimage."""

    def emit(self, record):
        """Maps the logger calls to call the specific Maya logging calls so the
        messages appear in the DCC as well.

        .. note::

            Calls to these Softimage specific methods are executed:
                - Application.LogMessage

        """

        msg = self.format(record)

        siLevel = constants.siComment
        if record.levelno == logging.CRITICAL:
            siLevel = constants.siFatal

        elif record.levelno == logging.ERROR:
            siLevel = constants.siError

        elif record.levelno == logging.WARNING:
            siLevel = constants.siWarning

        elif record.levelno == logging.INFORM:
            siLevel = constants.siInfo

        elif record.levelno == logging.INFO:
            siLevel = constants.siInfo

        elif record.levelno == logging.DEBUG:
            siLevel = constants.siVerbose

        else:
            siLevel = constants.siComment

        si.LogMessage(msg, siLevel)
