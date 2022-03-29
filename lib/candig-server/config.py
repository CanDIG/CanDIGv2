import os


OPA_SERVER = os.environ['OPA_SERVER']+"/v1/data/permissions/datasets"
OPA_SERVER_TOKEN = os.environ['OPA_SERVER_TOKEN']

TYK_ENABLED = True
TYK_SERVER = os.environ['TYK_SERVER']
TYK_LISTEN_PATH = os.environ['TYK_LISTEN_PATH']
ACCESS_LIST = "access_list.txt"
