import os, shutil, csv
from config import LIBLIST_FILE, LIB_DIR

def init():
    if os.path.isdir(LIB_DIR):
        shutil.rmtree(LIB_DIR)
    os.mkdir(LIB_DIR)
    with open(LIBLIST_FILE, "w") as f:
        w = csv.DictWriter(f, ["id", "name", "path"])
        w.writeheader()
