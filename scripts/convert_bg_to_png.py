import os
import struct

from helper import (
  DIR_BG_NCGR,
  DIR_BG_NCLR,
  DIR_BG_NSCR,
  DIR_TEMP_DECOMPRESSED,
  DIR_TEMP_IMAGES_BG,
  DIR_UNPACKED_FILES,
)
from nitrogfx.convert import NCGR, NCLR, NSCR, nclr_to_imgpal
from PIL import Image

BG_INFO_OFFSET = 0x00151BF4
BG_COUNT = 0x00F0

os.makedirs(DIR_TEMP_IMAGES_BG, exist_ok=True)

with open(f"{DIR_TEMP_DECOMPRESSED}/arm9.bin", "rb") as reader:
  reader.seek(BG_INFO_OFFSET)
  for i in range(BG_COUNT):
    nscr_index, ncgr_index, nclr_index = struct.unpack("<III", reader.read(0x0C))

    nscr: NSCR = NSCR.load_from(f"{DIR_UNPACKED_FILES}/{DIR_BG_NSCR}/{nscr_index:04d}.bin")
    ncgr: NCGR = NCGR.load_from(f"{DIR_UNPACKED_FILES}/{DIR_BG_NCGR}/{ncgr_index:04d}.bin")
    nclr: NCLR = NCLR.load_from(f"{DIR_UNPACKED_FILES}/{DIR_BG_NCLR}/{nclr_index:04d}.bin")

    pal = nclr_to_imgpal(nclr)
    image = Image.new("RGB", (nscr.width, nscr.height))
    for y in range(nscr.height // 8):
      for x in range(nscr.width // 8):
        entry = nscr.get_entry(x, y)
        tile = ncgr.tiles[entry.tile].flipped(entry.xflip, entry.yflip)
        tile_image = Image.frombytes("P", (8, 8), tile.get_data())
        tile_image.putpalette(pal[48 * entry.pal :])
        image.paste(tile_image, (x * 8, y * 8))

    image.save(f"{DIR_TEMP_IMAGES_BG}/{nscr_index:04d}.png")
