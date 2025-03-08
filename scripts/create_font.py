import json
import os
import struct
from typing import Callable

from helper import (
  CHAR_TABLE_PATH,
  DIR_DATA_FONT,
  DIR_TEMP_IMPORT,
  DIR_TEXT_FILES,
  DIR_UNPACKED_FILES,
  get_used_characters,
)
from nftr import CMAP, NFTR, CGLPTile
from PIL import Image, ImageDraw, ImageFont


def expand_font_0(old_font: NFTR) -> NFTR:
  old_font.finf.font_width = 12
  old_font.cglp.depth = 1
  old_font.cglp.tile_width = 12
  for tile in old_font.cglp.tiles:
    old_bitmap = tile.get_image()
    new_bitmap = Image.new("L", (12, 16), 0xFF)
    for y in range(16):
      for x in range(8):
        if old_bitmap.getpixel((x, y)) == 0xAA:
          new_bitmap.putpixel((x, y), 0x00)
    tile.width = 12
    tile.depth = 1
    tile.raw_bytes = tile.get_bytes(new_bitmap)

  return old_font


def expand_font_3(old_font: NFTR) -> NFTR:
  old_font.finf.font_width = 12
  old_font.cglp.tile_width = 12
  for tile in old_font.cglp.tiles:
    old_bitmap = tile.get_image()
    new_bitmap = Image.new("L", (12, 16), 0xFF)
    new_bitmap.paste(old_bitmap, (0, 0))
    tile.width = 12
    tile.raw_bytes = tile.get_bytes(new_bitmap)

  return old_font


def convert_font_4(old_font: NFTR) -> NFTR:
  old_font.cglp.depth = 1
  for tile in old_font.cglp.tiles:
    old_bitmap = tile.get_image()
    new_bitmap = Image.new("L", (12, 16), 0xFF)
    for y in range(16):
      for x in range(12):
        if old_bitmap.getpixel((x, y)) == 0xAA:
          new_bitmap.putpixel((x, y), 0x00)
    tile.depth = 1
    tile.raw_bytes = tile.get_bytes(new_bitmap)

  return old_font


def draw_char_0(bitmap: Image.Image, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  draw.text(
    (0, 12),
    char,
    0x00,
    font,
    "ls",
  )


def draw_char_3(bitmap: Image.Image, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  for x in range(-1, 2, 1):
    for y in range(-1, 2, 1):
      draw.text(
        (1 + x, 11 + y),
        char,
        0xCC,
        font,
        "ls",
      )
  draw.text(
    (1, 11),
    char,
    0x00,
    font,
    "ls",
  )
  for y in range(4, 12):
    new_pixel = 0x93
    if y in [7, 8]:
      new_pixel = 0x6F
    elif y in [10]:
      new_pixel = 0xB7
    for x in range(0, 12):
      pixel: int = bitmap.getpixel((x, y))
      if pixel == 0x00:
        bitmap.putpixel((x, y), new_pixel)


def draw_char_4(bitmap: Image.Image, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  draw.text(
    (0, 12),
    char,
    0x00,
    font,
    "ls",
  )


def draw_char_5(bitmap: Image.Image, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  draw.text(
    (0, 10),
    char,
    0x00,
    font,
    "ls",
  )


def draw_char_6(bitmap: Image.Image, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  draw.text(
    (0, 13),
    char,
    0x00,
    font,
    "ls",
    stroke_width=1,
    stroke_fill=0xCC,
  )


def draw_char_7(bitmap: Image.Image, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  draw.text(
    (0, 13),
    char,
    0x00,
    font,
    "ls",
    stroke_width=1,
    stroke_fill=0xCC,
  )


FONT_CONFIG: dict[int, dict] = {
  0: {
    "handle": expand_font_0,
    "font": "files/fonts/Zfull-GB.ttf",
    "size": 10,
    "draw": draw_char_0,
    "width": 10,
  },
  3: {
    "handle": expand_font_3,
    "font": "files/fonts/GuanZhi.ttf",
    "size": 8,
    "draw": draw_char_3,
    "width": 8,
    "length": 8,
  },
  4: {
    "handle": convert_font_4,
    "font": "C:/Windows/Fonts/simsun.ttc",
    "size": 12,
    "draw": draw_char_4,
    "width": 12,
  },
  5: {
    "font": "C:/Windows/Fonts/simsun.ttc",
    "size": 12,
    "draw": draw_char_5,
    "width": 12,
  },
  6: {
    "font": "files/fonts/SmileySans-Oblique.otf",
    "size": 14,
    "draw": draw_char_6,
    "width": 12,
  },
  7: {
    "font": "files/fonts/HYZongYiTiJF.ttf",
    "size": 15,
    "draw": draw_char_7,
    "width": 16,
  },
}


def compress_cmap(char_map: dict[int, int]) -> list[CMAP]:
  char_map = {k: v for k, v in char_map.items()}
  if char_map[0] == 0x20:
    char_map[0] = 0x5F

  cmaps = []
  type_2_index_map = {}

  for index, char_code in char_map.items():
    if char_code == 0x8140:  # full-width space
      type_2_index_map[0x20] = index  # space
    elif char_code == 0x824F:  # ０
      cmap = CMAP.get_blank()
      cmap.type_section = 0
      cmap.first_char_code = 0x30  # 0
      cmap.last_char_code = 0x39  # 9
      cmap.index_map = {0x30: index}
      cmaps.append(cmap)
    elif char_code == 0x8260:  # Ａ
      cmap = CMAP.get_blank()
      cmap.type_section = 0
      cmap.first_char_code = 0x41  # A
      cmap.last_char_code = 0x5A  # Z
      cmap.index_map = {0x41: index}
      cmaps.append(cmap)
    elif char_code == 0x8281:  # ａ
      cmap = CMAP.get_blank()
      cmap.type_section = 0
      cmap.first_char_code = 0x61  # a
      cmap.last_char_code = 0x7A  # z
      cmap.index_map = {0x61: index}
      cmaps.append(cmap)
      break

  char_index = 0
  char_map_len = len(char_map)
  while char_index < len(char_map):
    char_code = char_map[char_index]

    code_index_diff = char_code - char_index
    window = 0x20
    while (
      char_index + window < char_map_len and char_map[char_index + window] - (char_index + window) == code_index_diff
    ):
      window += 1
    if window > 0x20:
      cmap = CMAP.get_blank()
      cmap.type_section = 0
      cmap.first_char_code = char_code
      cmap.last_char_code = char_map[char_index + window - 1]
      cmap.index_map = {char_map[index]: index for index in range(char_index, char_index + window)}
      cmaps.append(cmap)
      char_index += window
      continue

    window = 0
    while char_index + window < char_map_len and char_map[char_index + window] - char_code <= window * 2:
      if char_index + window > 0 and char_map[char_index + window] - char_map[char_index + window - 1] > 0x10:
        break
      window += 1

    if window > 0x20:
      cmap = CMAP.get_blank()
      cmap.type_section = 1
      cmap.first_char_code = char_code
      cmap.last_char_code = char_map[char_index + window - 1]
      cmap.index_map = {char_map[index]: index for index in range(char_index, char_index + window)}
      cmaps.append(cmap)

      char_index += window
      continue

    type_2_index_map[char_code] = char_index
    char_index += 1
    continue

  cmap = CMAP.get_blank()
  cmap.type_section = 2
  cmap.first_char_code = min(type_2_index_map.values())
  cmap.last_char_code = 0xFFFF
  cmap.index_map = type_2_index_map
  cmaps.append(cmap)

  return cmaps


def create_font():
  with open(CHAR_TABLE_PATH, "r", -1, "utf8") as reader:
    char_table: dict[str, str] = json.load(reader)

  os.makedirs(f"{DIR_TEMP_IMPORT}/{DIR_DATA_FONT}", exist_ok=True)
  for file_name in os.listdir(f"{DIR_UNPACKED_FILES}/{DIR_DATA_FONT}"):
    font_index = int(file_name.split(".")[0])
    if font_index not in FONT_CONFIG:
      continue

    characters = get_used_characters(f"{DIR_TEXT_FILES}/zh_Hans", font_index)
    nftr = NFTR(f"{DIR_UNPACKED_FILES}/{DIR_DATA_FONT}/{file_name}")
    config = FONT_CONFIG[font_index]

    handle: Callable[[NFTR], NFTR] = config.get("handle")
    if handle:
      nftr = handle(nftr)

    font = ImageFont.truetype(config["font"], config["size"])
    draw_char: Callable[[Image.Image, ImageDraw.ImageDraw, ImageFont.FreeTypeFont, str], None] = config["draw"]
    nftr.finf.default_start = 0
    nftr.finf.default_width = config["width"]
    nftr.finf.default_length = config.get("length", config["width"])

    new_char_map = {}
    for code in sorted(nftr.char_map.keys()):
      char = nftr.char_map[code]
      if char < 0x889F:
        new_char_map[code] = char
      else:
        break

    nftr.cwdh.info = nftr.cwdh.info[:code]
    tile = nftr.cglp.tiles[0]
    for shift_jis, chs in char_table.items():
      if not (chs in characters and 0x4E00 <= ord(chs) <= 0x9FFF):
        continue

      new_char_map[code] = struct.unpack(">H", shift_jis.encode("cp932"))[0]

      bitmap = Image.new("L", (tile.width, tile.height), 0xFF)
      draw = ImageDraw.Draw(bitmap)
      draw_char(bitmap, draw, font, chs)
      new_tile = CGLPTile(tile.width, tile.height, tile.depth, tile.get_bytes(bitmap))
      if code < len(nftr.cglp.tiles):
        nftr.cglp.tiles[code] = new_tile
      else:
        nftr.cglp.tiles.append(new_tile)

      code += 1

    nftr.cmaps = compress_cmap(new_char_map)
    nftr.char_map = new_char_map

    new_bytes = nftr.get_bytes()
    with open(f"{DIR_TEMP_IMPORT}/{DIR_DATA_FONT}/{font_index:04d}.bin", "wb") as writer:
      writer.write(new_bytes)

    print(f"Saved font {font_index:04d}.bin ({len(new_char_map):4d} characters, {len(new_bytes) / 1024:2.2f} KiB)")


if __name__ == "__main__":
  create_font()
