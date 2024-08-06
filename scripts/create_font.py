import json
import os
import shutil
import struct
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

from helper import CHAR_TABLE_PATH, DIR_IMPORT_ROOT, DIR_FONT, DIR_UNPACKED_FILES
from nftr import NFTR, CGLPTile, CWDHInfo


def draw_char_0(draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  draw.text(
    (1, 13),
    char,
    0x55,
    font,
    "ls",
  )
  draw.text(
    (0, 12),
    char,
    0xAA,
    font,
    "ls",
  )


def draw_char_4(draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  draw.text(
    (1, 13),
    char,
    0x55,
    font,
    "ls",
  )
  draw.text(
    (0, 12),
    char,
    0xAA,
    font,
    "ls",
  )


def draw_char_5(draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  draw.text(
    (0, 10),
    char,
    0x00,
    font,
    "ls",
  )


def draw_char_6(draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  draw.text(
    (0, 13),
    char,
    0x00,
    font,
    "ls",
    stroke_width=1,
    stroke_fill=0xcc,
  )

def draw_char_7(draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, char: str) -> None:
  draw.text(
    (0, 13),
    char,
    0x00,
    font,
    "ls",
    stroke_width=1,
    stroke_fill=0xcc,
  )


FONT_CONFIG: dict[int, dict] = {
  0: {
    "font": "files/fonts/Zfull-GB.ttf",
    "size": 8,
    "draw": draw_char_0,
    "width": 8,
  },
  3: {
    "font": "files/fonts/Zfull-GB.ttf",
    "size": 8,
    "draw": draw_char_0,
    "width": 8,
  },
  4: {
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
    "width": 11,
  },
  7: {
    "font": "files/fonts/HYZongYiTiJF.ttf",
    "size": 15,
    "draw": draw_char_7,
    "width": 16,
  },
}

with open(CHAR_TABLE_PATH, "r", -1, "utf8") as reader:
  char_table: dict[str, str] = json.load(reader)

os.makedirs(f"{DIR_IMPORT_ROOT}/{DIR_FONT}", exist_ok=True)
for file_name in os.listdir(f"{DIR_UNPACKED_FILES}/{DIR_FONT}"):
  font_index = int(file_name.split(".")[0])
  if font_index not in FONT_CONFIG:
    shutil.copy(f"{DIR_UNPACKED_FILES}/{DIR_FONT}/{file_name}", f"{DIR_IMPORT_ROOT}/{DIR_FONT}/{font_index:04d}.bin")
    continue

  nftr = NFTR(f"{DIR_UNPACKED_FILES}/{DIR_FONT}/{file_name}")
  config = FONT_CONFIG[font_index]

  font = ImageFont.truetype(config["font"], config["size"])
  draw_char: Callable[[ImageDraw.ImageDraw, ImageFont.FreeTypeFont, str], None] = config["draw"]
  char_width: int = config["width"]

  new_char_map = {}
  for code in sorted(nftr.char_map.keys()):
    char = nftr.char_map[code]
    if char < 0x889f:
      new_char_map[code] = char
    else:
      break

  tile = nftr.cglp.tiles[0]
  for shift_jis, chs in char_table.items():
    if not 0x4e00 <= ord(chs) <= 0x9fff:
      continue
    new_char_map[code] = struct.unpack(">H", shift_jis.encode("cp932"))[0]

    bitmap = Image.new("L", (tile.width, tile.height), 0xff)
    draw = ImageDraw.Draw(bitmap)
    draw_char(draw, font, chs)
    new_tile = CGLPTile(tile.width, tile.height, tile.depth, tile.get_bytes(bitmap))
    if code < len(nftr.cglp.tiles):
      nftr.cglp.tiles[code] = new_tile
      nftr.cwdh.info[code] = CWDHInfo(0, char_width, char_width)
    else:
      nftr.cglp.tiles.append(new_tile)
      nftr.cwdh.info.append(CWDHInfo(0, char_width, char_width))

    code += 1

  nftr.char_map = new_char_map

  new_bytes = nftr.get_bytes()
  with open(f"{DIR_IMPORT_ROOT}/{DIR_FONT}/{font_index:04d}.bin", "wb") as writer:
    writer.write(new_bytes)
