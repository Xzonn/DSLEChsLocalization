import io
import json
import os
import struct

from helper import (
  DIR_MESSAGES,
  DIR_TEXT_FILES,
  DIR_UNPACKED_FILES,
  TRASH_PATTERN,
  TranslationItem,
)


def parse_messages(reader: io.BytesIO, sheet_name: str) -> list[TranslationItem]:
  output = []

  _, string_count = struct.unpack("<2I", reader.read(8))
  assert _ == 0

  for i in range(string_count):
    reader.seek(0x08 + 0x04 * i)
    start, end = struct.unpack("<2I", reader.read(8))
    reader.seek(start)
    if i < string_count - 1:
      raw_bytes = reader.read(end - start)
    else:
      raw_bytes = reader.read()

    message = raw_bytes.rstrip(b"\0").decode("cp932")

    item = {
      "index": i,
      "key": f"{sheet_name.replace('/', '_')}_{i:04d}",
      "original": message,
      "translation": message,
    }
    if TRASH_PATTERN.search(message):
      item["trash"] = True
    output.append(item)

  return output


def convert_messages_to_json(input_root: str, json_root: str, language: str):
  for root, dirs, files in os.walk(input_root):
    for file_name in files:
      if not file_name.endswith(".bin"):
        continue

      file_path = os.path.relpath(f"{root}/{file_name}", input_root)
      output_path = f"{json_root}/{language}/{file_path.removesuffix(".bin")}.json"
      sheet_name = file_path.removesuffix(".bin").replace("\\", "/")

      with open(f"{input_root}/{file_path}", "rb") as reader:
        parsed = parse_messages(reader, sheet_name)

      if len(parsed) > 0:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", -1, "utf8", None, "\n") as writer:
          json.dump(parsed, writer, ensure_ascii=False, indent=2)
        continue

      if os.path.exists(output_path):
        os.remove(output_path)


if __name__ == "__main__":
  convert_messages_to_json(f"{DIR_UNPACKED_FILES}/{DIR_MESSAGES}", DIR_TEXT_FILES, "ja")
