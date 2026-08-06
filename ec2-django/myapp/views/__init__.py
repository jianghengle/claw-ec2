from rest_framework.exceptions import PermissionDenied
import random, string, re
import os, subprocess
from datetime import datetime, timedelta


def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    return result.stdout

def run_cmd_only(cmd):
    subprocess.run(cmd, shell=True, capture_output=False, text=True, check=False)

def file_exists(path):
    try:
        run_cmd('ls ' + path)
        return True
    except:
        return False
