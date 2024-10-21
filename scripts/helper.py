import json
import logging
import os
import re
from typing import TypedDict

DIR_TEXT_FILES = "texts"
DIR_ORIGINAL_FILES = "original_files"
DIR_OUT = "out"
DIR_ARM9_PATCH = "arm9_patch"

DIR_FONT_FILES = "files/fonts"
DIR_IMAGES_BG_FILES = "files/images/BG"
DIR_IMAGES_SPR_FILES = "files/images/SPR"
DIR_MESSAGES = "data/MSG"
DIR_BG_NCGR = "data/BG_NCGR"
DIR_BG_NCLR = "data/BG_NCLR"
DIR_BG_NSCR = "data/BG_NSCR"
DIR_SPR_NCER = "data/SPR_NCER"
DIR_SPR_NCGR = "data/SPR_NCGR"
DIR_SPR_NCLR = "data/SPR_NCLR"
DIR_DATA_FONT = "data/FONT_NFTR"
DIR_UNPACKED_FILES = "unpacked"
DIR_TEMP_IMPORT = "temp/import"
DIR_TEMP_IMAGES_BG = "temp/images/BG"
DIR_TEMP_IMAGES_SPR = "temp/images/SPR"


DIR_TEMP_DECOMPRESSED = "temp/decompressed"
DIR_TEMP_DECOMPRESSED_MODIFIED = "temp/decompressed_mod"
DIR_TEMP_OUT = "temp/out"

OLD_CHAR_TABLE_PATH = "files/char_table.json"
CHAR_TABLE_PATH = "out/char_table.json"
BANNER_PATH = "original_files/banner.bin"
BANNER_OUT_PATH = "out/banner.bin"
SYMBOL_OUT_PATH = "out/symbols.txt"

ARM9_COMPRESSED_SIZE_OFFSET = 0xB9C
ARM9_NEW_STRING_OFFSET = 0x214C564


TRASH_PATTERN = re.compile(
  r"[＿]",
  re.DOTALL,
)
CONTROL_PATTERN = re.compile(r"\^[0-9A-Za-z]|%[ds]|~[CFcf][0-9\-]+")
KANA_PATTERN = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]+")

CHINESE_TO_JAPANESE = {
  "·": "・",
  "—": "ー",
  " ": "　",
  "+": "＋",
  "-": "－",
  "%": "％",
  "~": "～",
  ".": "．",
  ",": "，",
  "/": "／",
}


class TranslationItem(TypedDict):
  index: int
  key: str
  original: str
  translation: str
  suffix: str
  trash: bool
  untranslated: bool
  offset: int
  max_length: int


char_table_reversed: dict[str, str] = {}
zh_hans_no_code = set()


def load_translation_dict(path: str) -> dict[str, str]:
  with open(path, "r", -1, "utf8") as reader:
    translation_list: list[TranslationItem] = json.load(reader)

  translations = {}
  for item_dict in translation_list:
    if item_dict.get("trash", False):
      continue
    if item_dict.get("untranslated", False) and item_dict["original"] == item_dict["translation"]:
      continue
    translations[item_dict["key"]] = item_dict["translation"]

  return translations


def load_translation_items(path: str) -> list[TranslationItem]:
  with open(path, "r", -1, "utf8") as reader:
    translation_list = json.load(reader)

  return translation_list


def get_used_characters(json_root: str, font_index: int = None) -> set[str]:
  keys = []
  if font_index is not None:
    key_list_path = f"{DIR_FONT_FILES}/key_list_{font_index:04d}.txt"
    if os.path.exists(key_list_path):
      with open(f"{DIR_FONT_FILES}/key_list_{font_index:04d}.txt", "r", -1, "utf8") as reader:
        keys = reader.read().splitlines()

  characters = set()
  for root, dirs, files in os.walk(json_root):
    for file_name in files:
      if not file_name.endswith(".json"):
        continue

      translations = load_translation_dict(f"{root}/{file_name}")

      for key, content in translations.items():
        if keys and key not in keys:
          continue
        content = CONTROL_PATTERN.sub("", content).replace("\n", "")
        if KANA_PATTERN.search(content):
          continue

        for k, v in CHINESE_TO_JAPANESE.items():
          content = content.replace(k, v)

        for char in content:
          characters.add(char)

  return characters


class CharTable:
  def __init__(self, char_table_path: str):
    self.char_table = {}
    if os.path.exists(char_table_path):
      with open(char_table_path, "r", -1, "utf8") as reader:
        self.char_table: dict[str, str] = json.load(reader)
    else:
      logging.warning("Character table not found.")

    self.char_table_reversed: dict[str, str] = {v: k for k, v in self.char_table.items()}
    self.zh_hans_no_code = set()

  def convert_zh_hans_to_shift_jis(self, text: str) -> str:
    output = []
    i = 0
    while i < len(text):
      char = text[i]
      if char == "^":
        output.append(text[i : i + 2])
        i += 2
        continue
      elif char == "%" and i < len(text) - 1 and text[i + 1] in "ds":
        output.append(f"%{text[i + 1]}")
        i += 2
        continue
      elif char == "~":
        search = re.search(r"～[CFcf]([0-9\-]+)", text[i:])
        if search:
          output.append(f"~{search.group(1)}")
          i += search.end()
          continue

      char = CHINESE_TO_JAPANESE.get(char, char)
      if char in "0123456789":
        char = chr(ord(char) - ord("0") + ord("０"))
      elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        char = chr(ord(char) - ord("A") + ord("Ａ"))
      elif char in "abcdefghijklmnopqrstuvwxyz":
        char = chr(ord(char) - ord("a") + ord("ａ"))

      if char in self.char_table_reversed:
        output.append(self.char_table_reversed[char])
      else:
        try:
          char.encode("cp932")
          output.append(char)
        except UnicodeEncodeError:
          if char not in self.zh_hans_no_code:
            logging.warning(f"Char missing: {char}")
            self.zh_hans_no_code.add(char)
          output.append("？")

      i += 1

    return "".join(output)
