import json
import os
import struct

from helper import (
  CHAR_TABLE_PATH,
  DIR_MESSAGES,
  DIR_TEMP_IMPORT,
  DIR_TEXT_FILES,
  CharTable,
  TranslationItem,
  load_translation_dict,
)


def to_messages(data: dict[int, TranslationItem]) -> bytes:
  string_count = len(data)
  header = bytearray()
  body = bytearray()

  header.extend(struct.pack("<2I", 0, string_count))

  pos = 0x08 + 0x04 * string_count
  for k, v in data.items():
    header.extend(struct.pack("<I", pos))
    text = v["translation"].encode("cp932") + b"\0"
    text += b"\0" * (-len(text) % 4)
    body.extend(text)
    pos += len(text)

  return bytes(header + body)


def convert_json_to_messages(json_root: str, language: str, output_root: str, char_table: CharTable):
  for root, dirs, files in os.walk(f"{json_root}/ja"):
    for file_name in files:
      if "MESPAK" not in root or not file_name.endswith(".json"):
        continue

      file_path = os.path.relpath(f"{root}/{file_name}", f"{json_root}/ja")
      sheet_name = file_path.removesuffix(".json").replace("\\", "/")
      original_json_path = f"{json_root}/ja/{file_path}"
      translation_json_path = f"{json_root}/{language}/{file_path}"
      if not os.path.exists(original_json_path) or not os.path.exists(translation_json_path):
        continue

      with open(original_json_path, "r", -1, "utf-8") as reader:
        data_dict: dict[int, TranslationItem] = {i["index"]: i for i in json.load(reader)}

      translations = load_translation_dict(translation_json_path)
      for key, value in data_dict.items():
        if value["key"] in translations:
          value["translation"] = char_table.convert_zh_hans_to_shift_jis(translations[value["key"]])

      new_bytes = to_messages(data_dict)

      output_path = f"{output_root}/{sheet_name}.bin"
      os.makedirs(os.path.dirname(output_path), exist_ok=True)
      with open(output_path, "wb") as writer:
        writer.write(new_bytes)


if __name__ == "__main__":
  char_table = CharTable(CHAR_TABLE_PATH)
  convert_json_to_messages(DIR_TEXT_FILES, "zh_Hans", f"{DIR_TEMP_IMPORT}/{DIR_MESSAGES}", char_table)
