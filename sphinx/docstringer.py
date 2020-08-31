from pathlib import Path
import os
import re

entry_seperator = '='*25

class Replacer():

    def __init__(self, docstring_file):
        self.docstring_file = Path(docstring_file)
    
    def _read_docstrings(self):
        self._edited_docstrings = []
        with open(str(self.docstring_file)) as docstrings:
            try:
                while docstrings:
                    cur_line = next(docstrings)
                    if cur_line.strip() == entry_seperator:
                        cur_line = next(docstrings)
                        filepath, function = cur_line.strip().split(' | ')
                        edited_docstring = ''
                        cur_line = next(docstrings)
                        while docstrings and cur_line.strip() != entry_seperator:
                            edited_docstring += cur_line
                            cur_line = next(docstrings)
                        self._edited_docstrings.append([filepath, function, edited_docstring])
            except StopIteration:
                return self._edited_docstrings

    def replace_docstrings(self):
        for edited_docstring in self._edited_docstrings:

            filepath, function, edited_docstring = edited_docstring
            with open(filepath, 'r+') as handle:
                text = handle.read()
                function = function.replace('(', '\(')
                function = function.replace(')', '\)')
                function = function.replace('[', '\[')
                function = function.replace(']', '\]')
                regex_str = r"{}\s*?.('''[\s\S]*?''')".format(function)
                print(regex_str)
                docstring_finder = re.compile(regex_str)
                target_docstring = docstring_finder.search(text)
                if target_docstring:
                        #text.replace(target_docstring.group(1), edited_docstring)
                        print('found target')

class Collector():

    docstring_regex = re.compile(r"(def .+\(.+\):)\s*?.('''[\s\S]*?''')")
    excluded_dirs = set([])

    def __init__(self, parent_dir, output_path):
        self.parent_dir = Path(parent_dir)
        self.output_path = Path(output_path)
        self._docstring_record = open(str(
            self.output_path.joinpath('docstring_recs.txt')), 'w')

    def _collect_files(self):
        py_files = []

        def traverse(path):
            if path.is_dir():
                for handle in path.iterdir():
                    if handle.suffix == '.py':
                        py_files.append(handle)
                    elif handle.is_dir():
                        traverse(handle)

        traverse(self.parent_dir)
        return py_files
    

    def _docstring_header(self, filepath, function):
        return '{}\n{} | {}'.format(entry_seperator, filepath, function)
    
    def _write_docstring(self, filepath, regex_match):
        self._docstring_record.write(
            '{}\n{}\n{}\n'.format(
                self._docstring_header(filepath, regex_match[0]),
                regex_match[1],
                entry_seperator
            )
        )
    
    def _find_docstrings(self, filepath):
        with open(str(filepath)) as handle:
            print('Reading ', filepath)
            text = handle.read()
            print('Read', len(text), 'characters')
            docstrings = Collector.docstring_regex.findall(text)
            return docstrings

    def collect_docstrings(self):
        py_paths = self._collect_files()
        for each_py_path in py_paths:
            print('='*20)
            docstrings = self._find_docstrings(each_py_path)
            print('Found', len(docstrings), 'docstrings')
            for each_docstring in docstrings:
                self._write_docstring(each_py_path, each_docstring)
        self._docstring_record.close()



        

c = Collector('/home/ethan/Documents/github/Marco_Polo/src', '.')
c.collect_docstrings()
r = Replacer('/home/ethan/Documents/github/Marco_Polo/sphinx/docstring_recs.txt')
r._read_docstrings()
r.replace_docstrings()


        

        

            


