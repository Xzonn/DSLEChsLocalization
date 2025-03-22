import io
import json
import os

from helper import (
  DIR_TEMP_DECOMPRESSED,
  DIR_TEXT_FILES,
  TRASH_PATTERN,
  TranslationItem,
)

HARDCODED_TEXTS = {
  "arm9.bin": (
    ("こうげきりょく", "あたらしいワザをおぼえた！"),
    ("すべてのデジモン", "みとうろく"),
    ("だい%dファイル", "だい%dファイル"),
    ("こうげきりょく", "タイプ"),
  ),
  "overlay/overlay_0000.bin": (
    ("ごうけい", "しょじきん"),
    ("しょじきん", "しょじきん"),
  ),
}


def parse_binary(reader: io.BytesIO, sheet_name: str) -> list[TranslationItem]:
  output = []
  raw_bytes = reader.read()
  offset = 0
  for text_from, text_to in HARDCODED_TEXTS[f"{sheet_name}.bin"]:
    if type(text_from) is str:
      bytes_from = text_from.encode("cp932")
      bytes_to = text_to.encode("cp932")
    else:
      bytes_from = text_from
      bytes_to = text_to

    offset = raw_bytes.find(bytes_from, offset)
    if offset == -1:
      raise ValueError(f"String not found: {text_from}")

    while True:
      zero = raw_bytes.find(b"\x00", offset)
      if zero == -1:
        raise ValueError(f"String not terminated: {text_from}")
      text_bytes = raw_bytes[offset:zero]
      if len(text_bytes) == 0:
        offset = zero + 1
        continue

      message = text_bytes.decode("cp932")
      max_length = len(text_bytes) + (4 - len(text_bytes) % 4) - 1
      item: TranslationItem = {
        "offset": offset,
        "key": f"offset_{offset:08x}",
        "original": message,
        "translation": message,
        "max_length": max_length,
      }
      if TRASH_PATTERN.search(message):
        item["trash"] = True
      output.append(item)
      if text_bytes == bytes_to:
        break
      offset = zero + 1

  return output


def convert_binary_to_json(input_root: str, json_root: str, language: str):
  for key, value in HARDCODED_TEXTS.items():
    output_path = f"{json_root}/{language}/{key}.json"
    sheet_name = key.removesuffix(".bin").replace("\\", "/")
    with open(f"{input_root}/{key}", "rb") as reader:
      parsed = parse_binary(reader, sheet_name)

    if len(parsed) > 0:
      os.makedirs(os.path.dirname(output_path), exist_ok=True)
      with open(output_path, "w", -1, "utf8", None, "\n") as writer:
        json.dump(parsed, writer, ensure_ascii=False, indent=2)
      continue

    if os.path.exists(output_path):
      os.remove(output_path)


if __name__ == "__main__":
  convert_binary_to_json(DIR_TEMP_DECOMPRESSED, DIR_TEXT_FILES, "ja")
