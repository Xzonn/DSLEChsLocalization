import os
import struct

from helper import (
  DIR_BG_NCGR,
  DIR_BG_NCLR,
  DIR_BG_NSCR,
  DIR_IMAGES_BG_FILES,
  DIR_TEMP_DECOMPRESSED,
  DIR_TEMP_IMPORT,
  DIR_UNPACKED_FILES,
)
from nitrogfx.convert import (
  NCGR,
  NCLR,
  NSCR,
  Tile,
  TilesetBuilder,
  get_tile_data,
  nclr_to_imgpal,
)
from PIL import Image

BG_INFO_OFFSET = 0x00151BF4
BG_COUNT = 0x00F0

os.makedirs(f"{DIR_TEMP_IMPORT}/{DIR_BG_NCGR}", exist_ok=True)
os.makedirs(f"{DIR_TEMP_IMPORT}/{DIR_BG_NSCR}", exist_ok=True)

with open(f"{DIR_TEMP_DECOMPRESSED}/arm9.bin", "rb") as reader:
  reader.seek(BG_INFO_OFFSET)
  for i in range(BG_COUNT):
    nscr_index, ncgr_index, nclr_index = struct.unpack("<III", reader.read(0x0C))

    image_path = f"{DIR_IMAGES_BG_FILES}/{nscr_index:04d}.png"
    nscr_input_path = f"{DIR_UNPACKED_FILES}/{DIR_BG_NSCR}/{nscr_index:04d}.bin"
    nscr_output_path = f"{DIR_TEMP_IMPORT}/{DIR_BG_NSCR}/{nscr_index:04d}.bin"
    ncgr_input_path = f"{DIR_UNPACKED_FILES}/{DIR_BG_NCGR}/{ncgr_index:04d}.bin"
    ncgr_output_path = f"{DIR_TEMP_IMPORT}/{DIR_BG_NCGR}/{ncgr_index:04d}.bin"

    if not os.path.exists(image_path):
      continue

    nscr: NSCR = NSCR.load_from(nscr_input_path)
    nclr: NCLR = NCLR.load_from(f"{DIR_UNPACKED_FILES}/{DIR_BG_NCLR}/{nclr_index:04d}.bin")

    image = Image.open(image_path)
    if image.mode in {"RGBA", "P"}:
      image = image.convert("RGB")

    colors = nclr_to_imgpal(nclr)
    if nscr_index in {59, 60, 96}:
      ncgr: NCGR = NCGR.load_from(ncgr_input_path)
      for y in range(nscr.height // 8):
        for x in range(nscr.width // 8):
          entry = nscr.get_entry(x, y)
          if nscr_index == 59 and entry.tile == 3:
            continue
          palette = Image.new("P", (16, 16))
          palette.putpalette(colors[entry.pal * 48 : entry.pal * 48 + 48] * 16)
          tile_image = image.crop((x * 8, y * 8, x * 8 + 8, y * 8 + 8)).quantize(palette=palette)
          pixels = tile_image.load()
          tile = get_tile_data(pixels, 0, 0)
          ncgr.tiles[entry.tile] = tile.flipped(entry.xflip, entry.yflip)

      ncgr.save_as(ncgr_output_path)
    else:
      palette = Image.new("P", (16, 16))
      if len(colors) == 48:
        palette.putpalette(colors * 16)
      else:
        palette.putpalette(colors)

      image_converted = image.quantize(palette=palette)
      tileset = TilesetBuilder()
      tileset.add(Tile(b"\0" * 64))

      pixels = image_converted.load()
      for y in range(0, image_converted.height, 8):
        for x in range(0, image_converted.width, 8):
          tile = get_tile_data(pixels, x, y)
          nscr.set_entry(x // 8, y // 8, tileset.get_map_entry(tile))

      nscr.save_as(nscr_output_path)
      ncgr: NCGR = tileset.as_ncgr(8 if nscr.is8bpp else 4)
      ncgr.save_as(ncgr_output_path)

    print(f"NSCR: {nscr_index} (8bpp: {nclr.is8bpp}), NCGR: {ncgr_index}, NCLR: {nclr_index}")
