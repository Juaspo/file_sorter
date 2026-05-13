#!/usr/bin/env python3

import os
import shutil
from datetime import datetime

import yaml

import subprocess
import argparse
import sys

with open ("file_sort_config.yml", "r") as yml_file:
  cfg_file = yaml.safe_load(yml_file)


source_dir = "logs"
timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")

#pattern_matches = {"[test]": "/home/asante/code_cave/file_transfer/test_dir", "[old]": "old", "[new]": "new_dir"}
pattern_matches = cfg_file['files_to_sort']
check_folders = cfg_file["folders_to_check"]


file_paths = {"text", "./text_dir/",
              "audio", "./audio_dir",
              "picture", "./picture_dir"
              }


alg = ["md5sum", "sha1sum", "sha256sum", "sha512sum"]
provided_hash = None

argparser = argparse.ArgumentParser()
argparser.add_argument("-f", dest="file", type=str, help="Input file to calculate hash")
argparser.add_argument("-c", dest="hash", type=str, help="Hash string to compare with")
argparser.add_argument("-e", dest="encode", type=str, default=None, help="Encoding to use for hash calculation")
argparser.add_argument("-a", dest="algorithm", type=int, default=2, help="0=MD5, 1=SHA1, 2=SHA256 (def), 3=SHA512")
args = argparser.parse_args()

current_folder_to_check = check_folders["test_folder"]
if os.path.exists(current_folder_to_check):
  files = sorted(os.listdir(current_folder_to_check))
  print (files)

  for filename in files:
    for name_pattern in pattern_matches.keys():

      # Turn create tag name tag->[tag]
      file_tag = "[" + name_pattern + "]"
      if filename.startswith(file_tag):
      #if filename.startswith(name_pattern):

        target_dir = pattern_matches[name_pattern]
        if os.path.exists(target_dir):
          print("ok")
        else:
          try:
            #os.makedirs(os.path.abspath(target_dir), exist_ok=True)
            os.makedirs(target_dir, exist_ok=True)
            print("Directory '%s' created" % name_pattern)
          except OSError as error:
            print("Directory '%s' can not be created")
          
        new_filename = filename.replace(file_tag, "")
        dest_path = os.path.join(target_dir, new_filename)
        
        os.rename(os.path.join(current_folder_to_check, filename), dest_path)
        print(timestamp + " moved file " + filename + " to " + dest_path)

  files = [f for f in files if os.path.isfile(f)]
  print(*files, sep="\n")
else:
  print("Folder does not exist!: " + current_folder_to_check)

      
#source_path = os.path.join(source_dir, filename)


#print(list(cfg_file["files_to_sort"][new]))

#try:
#    # Check if source exists
#    if os.path.exists(source):
#        shutil.move(source, destination)
#        print("File move successful.")
#    else:
#        print(f"Error: The file {source} was not found.")
#except PermissionError:
#    print("Error: You don't have permission to move this file.")
#except shutil.Error as e:
#    print(f"A shutil error occurred: {e}")
#except Exception as e:
#    print(f"An unexpected error occurred: {e}")
#