import csv
import json
from logging import warning
import re

DIR_ORIGINAL_FILES = "original_files"
DIR_UNPACKED_FILES = "temp/unpacked"
DIR_MESSAGES = "data/MSG"
DIR_FONT = "data/FONT_NFTR/"
DIR_JSON_ROOT = "temp/json"
DIR_IMPORT_ROOT = "temp/import"
DIR_CSV_ROOT = "texts"
DIR_OUT = "out"
DIR_XLSX_ROOT = "out/xlsx"

ZH_HANS_2_KANJI_PATH = "files/zh_Hans_2_kanji.json"
CHAR_TABLE_PATH = "out/char_table.json"

TRASH_PATTERN = re.compile(
  #r"^[0-9a-zA-Z０-９ａ-ｚＡ-Ｚ#\-/？~№－\?:＋％%\.．ⅠⅡ <>_＿;，。！：；\n\+]+$|１２３４５６７８９|０１２３４５６７８",
  r"NULL",
  re.DOTALL,
)
KANA_PATTERN = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]+")

CHINESE_TO_JAPANESE = {
  "·": "・",
  "—": "ー",
  " ": "　",
  "-": "－",
}

char_table_reversed: dict[str, str] = {}
zh_hans_no_code = set()


def load_translations(root: str, sheet_name: str) -> dict[str, str]:
  with open(f"{root}/{sheet_name}.json", "r", -1, "utf8") as reader:
    translation_list: list[dict] = json.load(reader)

  translations = {}
  for item_dict in translation_list:
    translations[item_dict["key"]] = item_dict["translation"]

  return translations


def load_csv(root: str, sheet_name: str) -> list[dict[str, str]]:
  with open(f"{root}/{sheet_name}.json", "r", -1, "utf8") as reader:
    translation_list: list[dict] = json.load(reader)

  return translation_list


def convert_zh_hans_to_shift_jis(zh_hans: str) -> str:
  global char_table_reversed
  if len(char_table_reversed) == 0:
    with open(CHAR_TABLE_PATH, "r", -1, "utf8") as reader:
      char_table: dict[str, str] = json.load(reader)
      for k, v in char_table.items():
        char_table_reversed[v] = k

  output = []
  control = 0
  for char in zh_hans:
    if char == "^":
      control = 2
    if control > 0:
      output.append(char)
      control -= 1
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

  return "".join(output)
