import ftplib
import os
from pathlib import Path
from polo import make_default_logger

logger = make_default_logger(__name__)


def catch_ftp_errors(funct):
    '''General decorator function for catching any errors thrown by other
    ftp_utils functions.
    '''
    def try_function(*args, **kwargs):
        try:
            return funct(*args, **kwargs)
        except ftplib.all_errors as e:
            logger.error('Caught {} while calling {}'.format(funct))
            return e
    return try_function

@catch_ftp_errors
def logon(host, username, password, port=21):
    '''Attempts to connect to ftp server using the provided credentials.

    :param host: Host FTP server address
    :param username: Username of person attempting connection
    :param password: Password of person attempting connections
    :param port: Port to connect through. Default is 21.
    '''
    ftp = ftplib.FTP(host)
    ftp.login(username, password)
    return ftp
