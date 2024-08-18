import os
import struct

from helper import ARM9_DECOMPRESSED_PATH, DIR_BG_NCGR, DIR_BG_NCLR, DIR_BG_NSCR, DIR_TEMP_IMAGES_BG, DIR_UNPACKED_FILES
from nitrogfx.convert import NCGR, NCLR, NSCR, nscr_to_img

BG_INFO_OFFSET = 0x00151BF4
BG_COUNT = 0x00F0

os.makedirs(DIR_TEMP_IMAGES_BG, exist_ok=True)

with open(ARM9_DECOMPRESSED_PATH, "rb") as reader:
  reader.seek(BG_INFO_OFFSET)
  for i in range(BG_COUNT):
    nscr_index, ncgr_index, nclr_index = struct.unpack("<III", reader.read(0x0C))

    nscr: NSCR = NSCR.load_from(f"{DIR_UNPACKED_FILES}/{DIR_BG_NSCR}/{nscr_index:04d}.bin")
    ncgr: NCGR = NCGR.load_from(f"{DIR_UNPACKED_FILES}/{DIR_BG_NCGR}/{ncgr_index:04d}.bin")
    nclr: NCLR = NCLR.load_from(f"{DIR_UNPACKED_FILES}/{DIR_BG_NCLR}/{nclr_index:04d}.bin")

    image = nscr_to_img(ncgr, nscr, nclr)
    image.save(f"{DIR_TEMP_IMAGES_BG}/{nscr_index:04d}.png")
