import os
import shutil

from nitrogfx.convert import NCER, NCGR, NCLR, img_to_ncgr, ncgr_to_img, nclr_to_imgpal
from nitrogfx.ncer import OAM, Cell
from PIL import Image

from helper import (
  DIR_IMAGES_SPR_FILES,
  DIR_SPR_NCER,
  DIR_SPR_NCGR,
  DIR_TEMP_IMPORT,
)

SPR_COUNT = 0x0BD1

os.makedirs(f"{DIR_TEMP_IMPORT}/{DIR_SPR_NCER}", exist_ok=True)
os.makedirs(f"{DIR_TEMP_IMPORT}/{DIR_SPR_NCGR}", exist_ok=True)

for i in range(SPR_COUNT):
  ncer_path = f"{DIR_IMAGES_SPR_FILES}/{i:04d}.ncer"
  ncgr_path = f"{DIR_IMAGES_SPR_FILES}/{i:04d}.ncgr"
  png_path = f"{DIR_IMAGES_SPR_FILES}/{i:04d}.ncer_0.png"

  if os.path.exists(ncer_path):
    shutil.copy(ncer_path, f"{DIR_TEMP_IMPORT}/{DIR_SPR_NCER}/{i:04d}.bin")

  if os.path.exists(ncgr_path):
    shutil.copy(ncgr_path, f"{DIR_TEMP_IMPORT}/{DIR_SPR_NCGR}/{i:04d}.bin")

  if not os.path.exists(png_path):
    continue

  ncgr: NCGR = NCGR.load_from(f"temp/unpacked/data/SPR_NCGR/{i:04d}.bin")
  nclr: NCLR = NCLR.load_from(f"temp/unpacked/data/SPR_NCLR/{i:04d}.bin")
  ncer: NCER = NCER.load_from(f"temp/unpacked/data/SPR_NCER/{i:04d}.bin")

  old_image = ncgr_to_img(ncgr, nclr)
  new_image = old_image.convert("RGB")

  colors = nclr_to_imgpal(nclr)
  palette = Image.new("P", (16, 16))
  if len(colors) == 48:
    palette.putpalette(colors * 16)
  else:
    palette.putpalette(colors)

  cells: list[Cell] = ncer.cells
  for j, cell in enumerate(cells):
    png_path = f"{DIR_IMAGES_SPR_FILES}/{i:04d}.ncer_{j}.png"
    if not os.path.exists(png_path):
      continue

    cell_image = Image.open(png_path)
    if cell_image.size != (512, 256):
      continue
    if cell_image.mode in {"RGBA", "P"}:
      cell_image = cell_image.convert("RGB")

    oams: list[OAM] = cell.oam
    for k, oam in enumerate(oams):
      oam_width, oam_height = oam.get_size()
      x_offset = (oam.x + 0x100) % 0x200
      y_offset = (oam.y + 0x80) % 0x100

      if oam.colors == 16:
        Y = oam.char * 8 * 4 + cell.partition_offset // 4
      else:
        Y = oam.char * 8 * 2 + cell.partition_offset // 8

      oam_image = cell_image.crop((x_offset, y_offset, x_offset + oam_width, y_offset + oam_height))
      if oam.rot == 0:
        if (oam.rotsca >> 3) & 1:
          oam_image = oam_image.transpose(Image.FLIP_LEFT_RIGHT)
        if (oam.rotsca >> 4) & 1:
          oam_image = oam_image.transpose(Image.FLIP_TOP_BOTTOM)

      for y in range(0, oam_height, 8):
        for x in range(0, oam_width, 8):
          tile = oam_image.crop((x, y, x + 8, y + 8))
          new_image.paste(tile, (0, Y))
          Y += 8

    image_converted = new_image.quantize(palette=palette, dither=Image.NONE)
    new_ncgr = img_to_ncgr(image_converted, nclr.is8bpp)
    new_bytes = new_ncgr.pack()
    with open(f"{DIR_TEMP_IMPORT}/{DIR_SPR_NCGR}/{i:04d}.bin", "wb") as writer:
      with open(f"temp/unpacked/data/SPR_NCGR/{i:04d}.bin", "rb") as reader:
        writer.write(reader.read(0x30))
      writer.write(new_bytes[0x30:])
