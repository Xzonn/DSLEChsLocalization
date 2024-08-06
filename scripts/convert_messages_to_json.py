import json
import os
import struct
from typing import Any

from helper import DIR_UNPACKED_FILES, DIR_MESSAGES, DIR_JSON_ROOT, TRASH_PATTERN


def convert_messages_to_json(input_root: str, output_root: str):
  for root, dirs, files in os.walk(input_root):
    for file_name in files:
      if not file_name.endswith(".bin"):
        continue

      sheet_name = os.path.relpath(f"{root}/{file_name}", input_root).replace("\\", "/").removesuffix(".bin")

      output = {}
      reader = open(f"{root}/{file_name}", "rb")
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

        text = raw_bytes.rstrip(b"\0").decode("cp932")

        item = {
          "speaker": "",
          "content": text,
          "trash": TRASH_PATTERN.search(text) is not None,
        }

        output[f"{sheet_name.replace('/', '_')}_{i:04d}"] = item

      new_path = f"{output_root}/{sheet_name}.json"
      os.makedirs(os.path.dirname(new_path), exist_ok=True)
      with open(new_path, "w", -1, "utf8") as writer:
        writer.write(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  convert_messages_to_json(f"{DIR_UNPACKED_FILES}/{DIR_MESSAGES}", f"{DIR_JSON_ROOT}/ja")
