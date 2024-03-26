# Remove all raw.githubusercontent.com links from OpenAPI.yml files

import glob
import yaml
import subprocess
import re

# Find all yaml files
yml_files = glob.glob('lib/**/*.yml', root_dir='.', recursive=True)
yaml_files = glob.glob('lib/**/*.yaml', root_dir='.', recursive=True)
to_search = yml_files + yaml_files

TMP_FOLDER='/home/fnguyen/Documents/tmp'

# Recursively look for raw.githubusercontent.com links
gh_re = re.compile(r".+raw.githubusercontent.com/(.+?/.+?)/(.+)")
to_add = []
def look_for_links(obj):
    global to_add
    retval = {}
    for key, val in obj.items():
        if isinstance(val, dict):
            retval[key] = look_for_links(val)
        elif isinstance(val, str):
            url = gh_re.match(val)
            if url:
                to_add.append(url.groups())
                retval[key] = f"{TMP_FOLDER}/{url.groups()[0]}/{url.groups()[1]}"
        else:
            retval[key] = val
    return retval

# Look for raw.githubusercontent.com links
for filename in to_search:
    try:
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)
            out = look_for_links(config)
    except Exception as e:
        #print(f"Could not parse {filename}: {e}")
        pass

# Make a clone of everything we need
for to_clone in to_add:
    subprocess.Popen(f'git clone git@github.com:{to_clone[0]}.git', cwd=TMP_FOLDER, shell=True)

