import json
import os
import re
from logging import warning

DIR_ORIGINAL_FILES = "original_files"
DIR_FONT_FILES = "files/fonts"
DIR_IMAGES_BG_FILES = "files/images/BG"
DIR_IMAGES_SPR_FILES = "files/images/BG"
DIR_TEXT_FILES = "texts"
DIR_MESSAGES = "data/MSG"
DIR_BG_NCGR = "data/BG_NCGR"
DIR_BG_NCLR = "data/BG_NCLR"
DIR_BG_NSCR = "data/BG_NSCR"
DIR_DATA_FONT = "data/FONT_NFTR"
DIR_UNPACKED_FILES = "temp/unpacked"
DIR_TEMP_JSON = "temp/json"
DIR_TEMP_IMPORT = "temp/import"
DIR_TEMP_IMAGES_BG = "temp/images/BG"
DIR_TEMP_IMAGES_SPR = "temp/images/SPR"
DIR_OUT = "out"
DIR_XLSX = "out/xlsx"

OLD_CHAR_TABLE_PATH = "files/char_table.json"
CHAR_TABLE_PATH = "out/char_table.json"
ARM9_PATH = "original_files/arm9.bin"
ARM9_DECOMPRESSED_PATH = "src/arm9.bin"
ARM9_MODIFIED_PATH = "temp/nitro/arm9.bin"
ARM9_OUT_PATH = "out/arm9.bin"
BANNER_PATH = "original_files/banner.bin"
BANNER_OUT_PATH = "out/banner.bin"


TRASH_PATTERN = re.compile(
  # r"^[0-9a-zA-Z０-９ａ-ｚＡ-Ｚ#\-/？~№－\?:＋％%\.．ⅠⅡ <>_＿;，。！：；\n\+]+$|１２３４５６７８９|０１２３４５６７８",
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
}
HARDCODED_TEXTS_ARM9_BIN = [
  ("こうげきりょく", "あたらしいワザをおぼえた！"),
  ("すべてのデジモン", "みとうろく"),
  ("だい%dファイル", "だい%dファイル"),
  ("こうげきりょく", "タイプ"),
]

char_table_reversed: dict[str, str] = {}
zh_hans_no_code = set()


def load_translations(path: str) -> dict[str, str]:
  with open(path, "r", -1, "utf8") as reader:
    translation_list: list[dict] = json.load(reader)

  translations = {}
  for item_dict in translation_list:
    translations[item_dict["key"]] = item_dict["translation"]

  return translations


def load_csv(path: str) -> list[dict[str, str]]:
  with open(path, "r", -1, "utf8") as reader:
    translation_list: list[dict] = json.load(reader)

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

      translations = load_translations(f"{root}/{file_name}")

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


def convert_zh_hans_to_shift_jis(zh_hans: str) -> str:
  global char_table_reversed
  if len(char_table_reversed) == 0:
    with open(CHAR_TABLE_PATH, "r", -1, "utf8") as reader:
      char_table: dict[str, str] = json.load(reader)
      for k, v in char_table.items():
        char_table_reversed[v] = k

  for k, v in CHINESE_TO_JAPANESE.items():
    zh_hans = zh_hans.replace(k, v)

  output = []
  i = 0
  while i < len(zh_hans):
    char = zh_hans[i]
    if char == "^":
      output.append(zh_hans[i : i + 2])
      i += 2
      continue
    elif char == "％":
      search = re.search(r"％([ds])", zh_hans[i:])
      if search:
        output.append(f"%{search.group(1)}")
        i += search.end()
        continue
    elif char == "～":
      search = re.search(r"～[CFcf]([0-9\-]+)", zh_hans[i:])
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

    if char in char_table_reversed:
      output.append(char_table_reversed[char])
    else:
      try:
        char.encode("cp932")
        output.append(char)
      except UnicodeEncodeError:
        if char not in zh_hans_no_code:
          warning(f"Missing char: {char}")
          zh_hans_no_code.add(char)
        output.append("?")

    i += 1

  return "".join(output)
