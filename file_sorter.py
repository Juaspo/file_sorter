#!/usr/bin/env python3

import os
from datetime import datetime
import yaml
import argparse

yml_path = "file_sorter_config.yml"
result_output = ""
timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")

argparser = argparse.ArgumentParser()
argparser.add_argument("-f", dest="file", type=str, help="Input file to calculate hash")
argparser.add_argument("-c", dest="hash", type=str, help="Hash string to compare with")
argparser.add_argument("-e", dest="encode", type=str, default=None, help="Encoding to use for hash calculation")
argparser.add_argument("-a", dest="algorithm", type=int, default=2, help="0=MD5, 1=SHA1, 2=SHA256 (def), 3=SHA512")

argparser.add_argument("-v", "--verbose", type=str, help="Print runtime log")
argparser.add_argument("-t", "--tag", type=str, default=None, help="Use a specific tag for file sorter")
argparser.add_argument("-l", "--list", action="store_true", help="List files with tags")
args = argparser.parse_args()

# Get configuration from yaml file
if os.path.exists(yml_path):
  with open (yml_path, "r") as yml_file:
    cfg_file = yaml.safe_load(yml_file)

files_to_sort = cfg_file['files_to_sort']
folders_to_check = cfg_file["folders_to_check"]


for source_folder in folders_to_check:
  first_hit = True
  current_folder = folders_to_check[source_folder]
  if os.path.exists(current_folder):
    files_in_source_folder = sorted(os.listdir(current_folder))

    for filename in files_in_source_folder:
      for tag in files_to_sort.keys():

        # Create tag name tag->[tag]
        file_tag = "[" + tag + "]"
        if filename.startswith(file_tag):
          if(first_hit):
            result_output = result_output + "\t" + source_folder + "\n"
            first_hit = False
          if args.list:
            result_output = result_output + filename + "\n"
          else:
            target_dir = files_to_sort[tag]
            if os.path.exists(target_dir):
              print("ok")
            else:
              try:
                os.makedirs(target_dir, exist_ok=True)
                print("Directory '%s' created" % tag)
              except OSError as error:
                print("Directory '%s' can not be created")
              
            new_filename = filename.replace(file_tag, "")
            new_filename = new_filename.strip(' -_')
            dest_path = os.path.join(target_dir, new_filename)
            
            source_file = os.path.join(current_folder, filename)
            try:
              if os.path.exists(source_file):
                os.rename(source_file, dest_path)
                result_output = result_output + timestamp + " moved file " + filename + " to " + dest_path + "\n"
            except PermissionError:
                print("Error: You don't have permission to move this file")
            except FileNotFoundError:
                print(f"Error: The file {dest_path} was not found")
            except FileExistsError:
                print(f"Error: The file {dest_path} already exists")

  else:
    print("Folder does not exist!: " + current_folder)

print(current_folder + "\n" + result_output)
