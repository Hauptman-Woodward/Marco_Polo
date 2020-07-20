import platform
import os
from polo import UNRAR_EXE
import subprocess
from pathlib import Path

UNRAR_EXE = str(UNRAR_EXE)

def unrar_archive(rar_path, target_dir=None):
    '''De-compress a rar archive and return the path to the
    uncompressed archive if it exists. All unrar functions
    including this one are dependent of their being a working 
    unrar installation. Unrar is included for both Windows and Mac
    operating systems but not for Linux.

    :param rar_path: Path to rar archive file
    :type rar_path: Path or str
    :param target_dir: Location to place the unrared file, defaults to None
    :type target_dir: Path or str, optional
    :return: Path if unrar is successful, error code if unrar fails or Exception if
    exception is raised in the unrar process.
    :rtype: Path, str or Exception
    '''
    try:
        unrar_cmd = [UNRAR_EXE, 'x', '-y', str(rar_path), str(target_dir)]
        exit_status = subprocess.call(unrar_cmd)

        if exit_status == 0:
            return Path(str(rar_path)).with_suffix('')
        else:
            return exit_status
    except Exception as e:
        return e
        # do some exception handling here

# def parse_check_file_output(output_bytes):
#     files = set([])
#     output_string = str(output_bytes, 'utf-8')
#     lines = output_string.split('\n')
#     for l in lines:
#         if l:
#             l = l.split('     ')
#             if len(l) == 3:
#                 files.add(l[0])  # add the file name to set
#     return files

# def test_file_contents(rar_path):
#     try:
#         check_cmd = [UNRAR_EXE, 't', rar_path]
#         output = subprocess.check_output(check_cmd)
#     except Exception as e:
#         pass

def test_for_working_unrar(unrar_exe=UNRAR_EXE):
    '''Tests if a working unrar installation exists on the machine.

    :param unrar_exe: Path to unrar executable file, defaults to UNRAR_EXE
    :type unrar_exe: Path or str, optional
    :return: True if working installation exists, False otherwise
    :rtype: bool
    '''
    if unrar_exe:
        try:
            exit_status = subprocess.call([UNRAR_EXE], stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
            if exit_status == 0:
                return True
            else:
               return False
        except Exception as e:
            return False
    else:
        return False



