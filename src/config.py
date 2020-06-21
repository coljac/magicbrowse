import os
import coltools as ct

config = {}

config['images_dir'] = "/home/coljac/Pictures/mtg/"
if os.path.exists("mtgcards.cfg"):
   lines = ct.fal("mtgcards.cfg")
   for line in lines:
      key, val = line.strip().split(",")
      config[key] = val

def save_config():
   save = ""
   for key, val in config.items():
      save += "%s,%s\n" % (key, val)
   ct.strf("mtgcards.cfg", save)
