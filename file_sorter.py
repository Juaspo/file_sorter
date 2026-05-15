#!/usr/bin/env python3

import os
from datetime import datetime
import yaml
import argparse
import shutil


yml_file = "file_sorter_config.yml"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
result_output = f"\n###\tsort action {timestamp} \t###\n"
file_moved = 0
file_error = 0
file_renamed = 0

argparser = argparse.ArgumentParser()
argparser.add_argument("-s", "--source", dest="check_source", default=None, type=str, help="Check a specific source dir")
argparser.add_argument("-v", "--verbose", action="store_true", help="Print runtime log")
#argparser.add_argument("-t", "--tag", type=str, default=None, help="Use a specific tag for file sorter")
argparser.add_argument("-l", "--list", action="store_true", help="List files with tags")
argparser.add_argument("-y", "--yaml", action="store_true", help="print yaml config file")
args = argparser.parse_args()

# Definition to add text to log
def addToLog(logtext, new_line=False):
  global result_output
  result_output = result_output + logtext
  if (new_line):
    result_output = result_output + "\n"

# Definition to remove tag from filename e.g [tag]filename.txt -> filename.txt
def trimName(file_tag, filename):
  new_filename = filename.replace(file_tag, "")
  new_filename = new_filename.strip(' -_')
  return new_filename

# Definition for handling movement and renaming of files
def moveFile(source_path, destination_path, filename, newname=None):
  global file_moved
  global file_error
  global file_renamed
  full_source = os.path.join(source_path, filename)
  full_destination = os.path.join(destination_path, filename)

  if os.path.exists(source_path):
    if os.path.exists(full_destination):
      file_error = file_error + 1
      return (f"Error: Destination file already exist: {full_destination}")
    else:
      try:
        # move the actual file
        shutil.move(full_source, full_destination)
        file_moved = file_moved + 1
        if (newname is not None):
          new_name = os.path.join(destination_path, newname)
          if (os.path.exists(new_name)):
            file_error = file_error + 1
            return (f"Error: The file {newname} already exists, Cannot rename file {full_destination}")
          else:
            os.rename(full_destination, new_name)
            file_renamed = file_renamed + 1
      except PermissionError:
        file_error = file_error + 1
        print("Error: You don't have permission to move this file.")
        return("Error: You don't have permission to move this file.")
      except shutil.Error as e:
        file_error = file_error + 1
        print(f"A shutil error occurred: {e}")
        return(f"A shutil error occurred: {e}")
      except Exception as e:
        file_error = file_error + 1
        print(f"An unexpected error occurred: {e}")
        return(f"An unexpected error occurred: {e}")
  else:
    file_error = file_error + 1
    return (f"Source file cannot be found: {source_path}")
  return (f"moved from {source_path} to {destination_path} file:{filename}->{newname}")

# Get configuration from yaml file
dir_path = os.path.dirname(os.path.abspath(__file__)) # get absolute path of current script dir
yml_path = os.path.join(dir_path, yml_file)
if os.path.exists(yml_path):
  with open (yml_path, "r") as yml_file:
    yaml_content = yml_file.read()
    cfg_file = yaml.safe_load(yaml_content)
  if args.yaml:
    print(yaml_content)
    raise SystemExit(0)
else:
  print (f"ERROR: Missing yaml config file: {yml_path}")
  raise SystemExit(0)

specific_folder = args.check_source
if specific_folder is not None: # If a specific folder is passed as argument only serach that folder
  folders_to_check = {specific_folder: cfg_file["folders_to_check"][specific_folder]}
else: # Else use defined folders from yaml
  folders_to_check = cfg_file["folders_to_check"]
tag_chars = [cfg_file["tag_sign"]["start_sign"], cfg_file["tag_sign"]["end_sign"]]
tags_to_sort = cfg_file["tags_to_sort"] # get tags from yaml file
log_file_path = cfg_file["log_output_path"]
if log_file_path == "default": # If default value is given by yaml, set path to same as script
  log_file_path = __file__.rsplit('.', 1)[0] + '.log'

for source_folder in folders_to_check:
  first_hit = True # Reset new source folder trigger
  current_source = folders_to_check[source_folder]
  if os.path.exists(current_source):
    files_in_source_folder = sorted(os.listdir(current_source))
    for filename in files_in_source_folder:
      for tag in tags_to_sort.keys():

        # Format tag to similar as file tag name. tag->[tag]
        file_tag = tag_chars[0] + tag + tag_chars[1]
        if filename.startswith(file_tag):
          if(first_hit): # If new source folder, add folder name title to log
            folder_title = "\t" + source_folder + "\n"
            addToLog(folder_title)
            first_hit = False
          if args.list:
            addToLog(filename, True)
          else:
            target_dir = tags_to_sort[tag]
            try:
              os.makedirs(target_dir, exist_ok=True)
            except OSError as error:
              addToLog(f"Directory can not be created: {target_dir}\n")
              file_error = file_error + 1

            new_filename = trimName(file_tag, filename)
            if os.path.exists(target_dir):
              move_log = (moveFile(current_source, target_dir, filename, new_filename))
              addToLog(move_log, True)

  else:
    print("Error: Folder does not exist!: " + current_source)
    addToLog("Error: Folder does not exist!: " + current_source)
    file_error = file_error + 1

if args.verbose:
  print(result_output)
if not args.list:
  print(f"file moved:   {file_moved}")
  print(f"file renamed: {file_renamed}")
  print(f"file errors:  {file_error}")
  addToLog(f"file moved:   {file_moved}", True)
  addToLog(f"file renamed: {file_renamed}", True)
  addToLog(f"file errors:  {file_error}", True)
  with open(log_file_path, "a") as log_f:
      log_f.write(result_output)

print(f"Logfile at:{log_file_path}\nFile sorter finished!")
