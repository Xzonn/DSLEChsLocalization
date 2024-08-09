import os
import struct
from nitrogfx.convert import *

from helper import ARM9_DECOMPRESSED_PATH

BG_INFO_OFFSET = 0x00151BF4
BG_COUNT = 0x00F0
SPR_COUNT = 0x0BD1

os.makedirs(f"temp/images/BG", exist_ok=True)
os.makedirs(f"temp/images/SPR", exist_ok=True)

with open(ARM9_DECOMPRESSED_PATH, "rb") as reader:
  reader.seek(BG_INFO_OFFSET)
  for i in range(BG_COUNT):
    nscr_index, ncgr_index, nclr_index = struct.unpack("<III", reader.read(0x0C))

    nscr: NSCR = NSCR.load_from(f"temp/unpacked/data/BG_NSCR/{nscr_index:04d}.bin")
    ncgr: NCGR = NCGR.load_from(f"temp/unpacked/data/BG_NCGR/{ncgr_index:04d}.bin")
    nclr: NCLR = NCLR.load_from(f"temp/unpacked/data/BG_NCLR/{nclr_index:04d}.bin")

    image = nscr_to_img(ncgr, nscr, nclr)
    image.save(f"temp/images/BG/{nscr_index:04d}.png")

for i in range(SPR_COUNT):
  ncgr: NCGR = NCGR.load_from(f"temp/unpacked/data/SPR_NCGR/{i:04d}.bin")
  nclr: NCLR = NCLR.load_from(f"temp/unpacked/data/SPR_NCLR/{i:04d}.bin")
  ncer: NCER = NCER.load_from(f"temp/unpacked/data/SPR_NCER/{i:04d}.bin")

  image = ncgr_to_img(ncgr, nclr)
  cells: list[Cell] = ncer.cells

  for j, cell in enumerate(cells):
    oams: list[OAM] = cell.oam
    cell_width: int = cell.max_x - cell.min_x + 1
    cell_height: int = cell.max_y - cell.min_y + 1
    cell_image = Image.new("RGBA", (cell_width, cell_height))
    for k, oam in enumerate(oams):
      oam_width, oam_height = oam.get_size()
      x_offset = oam.x - cell.min_x
      if oam.x > cell.max_x:
        x_offset -= 0x200
      y_offset = oam.y - cell.min_y
      if oam.y > cell.max_y:
        y_offset -= 0x100

      Y = oam.char * 8 * (4 if oam.colors == 16 else 2)
      if cell.partition_offset > 0:
        Y += cell.partition_offset // cell.partition_size * cell_width * cell_height // 8

      for y in range(0, oam_height, 8):
        for x in range(0, oam_width, 8):
          tile = image.crop((0, Y, 8, Y + 8))
          cell_image.paste(tile, (x_offset + x, y_offset + y))
          Y += 8

    cell_image.save(f"temp/images/SPR/{i:04d}_{j:02d}.png")
