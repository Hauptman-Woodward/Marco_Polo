import platform
import os
from polo import UNRAR_EXE
import subprocess
from pathlib import Path


class UnrarManager():

    unrar_exe = UNRAR_EXE

    def __init__(self):
        self.unrared_files = {}  # keep track of unrared files here

    def unrar_file(self, rar_path, target_dir):
        try:
            unrar_cmd = [self.unrar_exe, 'x', rar_path, target_dir]
            exit_status = subprocess.call(unrar_cmd)
            return exit_status
        except Exception as e:
            pass
        # do some exception handling here

    def parse_check_file_output(self, output_bytes):
        files = set([])
        output_string = str(output_bytes, 'utf-8')
        lines = output_string.split('\n')
        for l in lines:
            if l:
                l = l.split('     ')
                if len(l) == 3:
                    files.add(l[0])  # add the file name to set
        return files

    def get_file_contents(self, rar_path):
        try:
            check_cmd = [self.unrar_exe, 't', rar_path]
            output = subprocess.check_output(check_cmd)
