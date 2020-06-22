import ftplib
from pathlib import Path
import os


def catch_ftp_errors(funct):
    '''
    General decorator function for catching any errors thrown by other
    ftp_utils functions
    '''
    def try_function(*args, **kwargs):
        try:
            return funct(*args, **kwargs)
        except ftplib.all_errors as e:
            return e
    return try_function


@catch_ftp_errors
def logon(host, username, password, port=21):
    '''
    Attempts to connect to ftp server using the provided credentials on port
    21 by default.

    :param host: Host FTP server address
    :param username: Username of person attempting connection
    :param password: Password of person attempting connections
    :param port: Port to connect through. Default is 21.
    '''
    ftp = ftplib.FTP(host)
    ftp.login(username, password)
    return ftp


@catch_ftp_errors
def list_dir(ftp, dir=None):
    if dir:
        return ftp.dir(dir)
    else:
        return ftp.dir()


@catch_ftp_errors
def get_cwd(ftp):
    return ftp.cwd()
