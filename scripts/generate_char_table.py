import json
import os
import struct
from helper import DIR_TEXT_FILES, CHAR_TABLE_PATH, OLD_CHAR_TABLE_PATH, get_used_characters

import pypinyin
from pypinyin import lazy_pinyin

LANGUAGE = os.getenv("XZ_LANGUAGE") or "zh_Hans"


def generate_cp932(used_kanjis: set[str]):
  for high in range(0x88, 0xa0):
    for low in range(0x40, 0xfd):
      if low == 0x7f:
        continue
      code = (high << 8) | low
      try:
        char = struct.pack(">H", code).decode("cp932")
        if char in used_kanjis:
          continue
      except:
        continue
      yield char


def generate_char_table(old_char_table: dict[str, str], json_root: str) -> dict[str, str]:
  char_table: dict[str, str] = {**old_char_table}
  shift_jis_characters = set(char_table.keys())

  characters = get_used_characters(json_root) - set(char_table.values())
  generator = generate_cp932(set())

  def insert_char(char: str):
    shift_jis_char = next(generator)
    while shift_jis_char in shift_jis_characters:
      shift_jis_char = next(generator)
    char_table[shift_jis_char] = char
    shift_jis_characters.add(shift_jis_char)

  for char in sorted(characters, key=lambda x: (lazy_pinyin(x, style=pypinyin.Style.TONE3), x)):
    if 0x4e00 <= ord(char) <= 0x9fff:
      insert_char(char)

  char_table = {k: v for k, v in sorted(char_table.items(), key=lambda x: x[0].encode("cp932").rjust(2, b"\0"))}
  return char_table


if __name__ == "__main__":
  with open(OLD_CHAR_TABLE_PATH, "r", -1, "utf8") as reader:
    old_char_table = json.load(reader)
  char_table = generate_char_table(old_char_table, f"{DIR_TEXT_FILES}/{LANGUAGE}")
  os.makedirs(os.path.dirname(CHAR_TABLE_PATH), exist_ok=True)
  with open(CHAR_TABLE_PATH, "w", -1, "utf8") as writer:
    json.dump(char_table, writer, ensure_ascii=False, indent=2)
  print(f"Collected {len(char_table)} characters.")
