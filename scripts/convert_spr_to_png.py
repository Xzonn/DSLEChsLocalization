import os

from nitrogfx.convert import NCER, NCGR, NCLR, ncgr_to_img
from nitrogfx.ncer import OAM, Cell
from PIL import Image

SPR_COUNT = 0x0BD1

os.makedirs("temp/images/SPR", exist_ok=True)

for i in range(SPR_COUNT):
  ncgr: NCGR = NCGR.load_from(f"temp/unpacked/data/SPR_NCGR/{i:04d}.bin")
  nclr: NCLR = NCLR.load_from(f"temp/unpacked/data/SPR_NCLR/{i:04d}.bin")
  ncer: NCER = NCER.load_from(f"temp/unpacked/data/SPR_NCER/{i:04d}.bin")

  image = ncgr_to_img(ncgr, nclr)
  cells: list[Cell] = ncer.cells

  for j, cell in enumerate(cells):
    oams: list[OAM] = cell.oam
    cell_image = Image.new("RGBA", (512, 256))
    for k, oam in enumerate(oams):
      oam_width, oam_height = oam.get_size()
      x_offset = (oam.x + 0x100) % 0x200
      y_offset = (oam.y + 0x80) % 0x100

      if oam.colors == 16:
        Y = oam.char * 8 * 4 + cell.partition_offset // 4
      else:
        Y = oam.char * 8 * 2 + cell.partition_offset // 8

      oam_image = Image.new("RGBA", (oam_width, oam_height))
      for y in range(0, oam_height, 8):
        for x in range(0, oam_width, 8):
          tile = image.crop((0, Y, 8, Y + 8))
          oam_image.paste(tile, (x, y))
          Y += 8

      if oam.rot == 0:
        if (oam.rotsca >> 3) & 1:
          oam_image = oam_image.transpose(Image.FLIP_LEFT_RIGHT)
        if (oam.rotsca >> 4) & 1:
          oam_image = oam_image.transpose(Image.FLIP_TOP_BOTTOM)
      cell_image.paste(oam_image, (x_offset, y_offset))

    cell_image.save(f"temp/images/SPR/{i:04d}.ncer_{j}.png")
