import json
import logging
import os
import struct

from helper import (
  ARM9_NEW_STRING_OFFSET,
  CHAR_TABLE_PATH,
  DIR_TEMP_DECOMPRESSED,
  DIR_TEMP_DECOMPRESSED_MODIFIED,
  DIR_TEXT_FILES,
  CharTable,
  TranslationItem,
  load_translation_dict,
)


def to_binary(old_bytes: bytes, data: dict[int, TranslationItem]) -> bytes:
  output = bytearray(old_bytes)
  new_offset = ARM9_NEW_STRING_OFFSET
  for offset, item in data.items():
    text = item["translation"]
    text_bytes = text.encode("cp932")
    if len(text_bytes) > item["max_length"]:
      logging.warning(f"Text is too long: {text}")
      if item["key"].startswith("OVERLAY"):
        continue

      offset_bytes = struct.pack("<I", offset + 0x2000000)
      new_offset_bytes = struct.pack("<I", new_offset + 0x2000000)
      offset_offset = old_bytes.find(offset_bytes)
      while offset_offset != -1:
        output[offset_offset : offset_offset + 4] = new_offset_bytes
        offset_offset = old_bytes.find(offset_bytes, offset_offset + 4)

      new_length = len(text_bytes) + (4 - len(text_bytes) % 4) - 1
      text_bytes += b"\0" * (new_length - len(text_bytes))
      output[new_offset : new_offset + new_length] = text_bytes
      new_offset += new_length + 1
      continue

    text_bytes += b"\0" * (item["max_length"] - len(text_bytes))
    output[offset : offset + item["max_length"]] = text_bytes

  return bytes(output)


def convert_json_to_binary(json_root: str, language: str, original_root: str, output_root: str, char_table: CharTable):
  for root, dirs, files in os.walk(f"{json_root}/ja"):
    for file_name in files:
      if not file_name.endswith(".bin.json"):
        continue
      file_path = os.path.relpath(f"{root}/{file_name}", f"{json_root}/ja")
      sheet_name = file_path.removesuffix(".bin.json").replace("\\", "/")
      original_path = f"{original_root}/{sheet_name}.bin"
      original_json_path = f"{json_root}/ja/{file_path}"
      translation_json_path = f"{json_root}/{language}/{file_path}"
      if not os.path.exists(original_json_path) or not os.path.exists(translation_json_path):
        continue

      with open(original_json_path, "r", -1, "utf-8") as reader:
        data_dict: dict[int, TranslationItem] = {i["offset"]: i for i in json.load(reader)}

      translations = load_translation_dict(translation_json_path)

      for key, value in data_dict.items():
        if value["key"] in translations:
          value["translation"] = char_table.convert_zh_hans_to_shift_jis(translations[value["key"]])

      with open(original_path, "rb") as reader:
        old_bytes = reader.read()

      new_bytes = to_binary(old_bytes, data_dict)

      output_path = f"{output_root}/{sheet_name}.bin"
      os.makedirs(os.path.dirname(output_path), exist_ok=True)
      with open(output_path, "wb") as writer:
        writer.write(new_bytes)


if __name__ == "__main__":
  char_table = CharTable(CHAR_TABLE_PATH)
  convert_json_to_binary(DIR_TEXT_FILES, "zh_Hans", DIR_TEMP_DECOMPRESSED, DIR_TEMP_DECOMPRESSED_MODIFIED, char_table)
