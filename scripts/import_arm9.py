import json
import os
from logging import warning
from typing import Any

from helper import ARM9_MODIFIED_PATH, DIR_TEMP_JSON

LANGUAGE = os.getenv("XZ_LANGUAGE") or "zh_Hans"


def import_arm9(input_path: str, sheet_name: str, message_root: str, output_path: str):
  with open(input_path, "rb") as reader:
    binary = bytearray(reader.read())

  with open(f"{message_root}/{sheet_name}.json", "r", -1, "utf8") as reader:
    translations: dict[str, dict[str, Any]] = json.load(reader)

  for key, value in translations.items():
    offset: int = value["offset"]
    length: int = value["length"]
    text: str = value["content"]
    text_bytes = text.encode("cp932")
    if len(text_bytes) > length:
      warning(f"Text is too long: {text} ({key}, {len(text_bytes)} > {length})")
      continue
    elif len(text_bytes) < length:
      text_bytes += b"\0" * (length - len(text_bytes))

    binary[offset : offset + length] = text_bytes

  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  with open(output_path, "wb") as writer:
    writer.write(binary)


if __name__ == "__main__":
  import_arm9(
    ARM9_MODIFIED_PATH,
    "arm9.bin",
    f"{DIR_TEMP_JSON}/{LANGUAGE}",
    ARM9_MODIFIED_PATH,
  )
