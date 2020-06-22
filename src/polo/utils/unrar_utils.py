import platform
import os
from polo import UNRAR_EXE
import subprocess
from pathlib import Path

UNRAR_EXE = str(UNRAR_EXE)

def unrar_archive(rar_path, target_dir):
    try:
        unrar_cmd = [UNRAR_EXE, 'x', '-y', str(rar_path), str(target_dir)]
        exit_status = subprocess.call(unrar_cmd)

        if exit_status == 0:
            return Path(rar_path).with_suffix('')
        else:
            return exit_status
    except Exception as e:
        return e
        # do some exception handling here

def parse_check_file_output(output_bytes):
    files = set([])
    output_string = str(output_bytes, 'utf-8')
    lines = output_string.split('\n')
    for l in lines:
        if l:
            l = l.split('     ')
            if len(l) == 3:
                files.add(l[0])  # add the file name to set
    return files

def test_file_contents(rar_path):
    try:
        check_cmd = [UNRAR_EXE, 't', rar_path]
        output = subprocess.check_output(check_cmd)
    except Exception as e:
        pass

def test_for_working_unrar(unrar_exe=UNRAR_EXE):
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



