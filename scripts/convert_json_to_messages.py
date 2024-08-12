import json
import os
import struct
from helper import DIR_JSON_ROOT, DIR_IMPORT_ROOT, DIR_MESSAGES

LANGUAGE = os.getenv("XZ_LANGUAGE") or "zh_Hans"


def convert_json_to_messages(json_root: str, output_root: str):
  for root, dirs, files in os.walk(json_root):
    for file_name in files:
      if not file_name.endswith(".json"):
        continue

      sheet_name = os.path.relpath(f"{root}/{file_name}", json_root).replace("\\", "/").removesuffix(".json")

      with open(f"{root}/{file_name}", "r", -1, "utf8") as reader:
        translations: dict[str, dict] = json.load(reader)

      output_path = f"{output_root}/{sheet_name}.bin"
      os.makedirs(os.path.dirname(output_path), exist_ok=True)

      string_count = len(translations)
      header = bytearray()
      body = bytearray()
      pos = 0x08 + 0x04 * string_count
      for k, v in translations.items():
        header += struct.pack("<I", pos)
        text = v["content"].encode("cp932") + b"\0"
        text += b"\0" * (-len(text) % 4)
        body += text
        pos += len(text)

      with open(output_path, "wb") as writer:
        writer.write(struct.pack("<2I", 0, string_count))
        writer.write(header)
        writer.write(body)
        writer.close()


if __name__ == "__main__":
  convert_json_to_messages(f"{DIR_JSON_ROOT}/{LANGUAGE}", f"{DIR_IMPORT_ROOT}/{DIR_MESSAGES}")
