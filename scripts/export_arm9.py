import json
import os
from typing import Any
from helper import ARM9_DECOMPRESSED_PATH, DIR_TEMP_JSON, HARDCODED_TEXTS_ARM9_BIN, TRASH_PATTERN


def export_arm9(input_path: str, sheet_name: str, message_root: str, hardcoded_texts: list[tuple[str, str]]):

  def find_strings(binary: bytes, output: dict[str, dict[str, Any]], start: str | bytes, end: str | bytes, start_index: int = 0):
    if type(start) is str:
      start_bytes = start.encode("cp932") + b"\0"
    else:
      start_bytes = start + b"\0"

    if type(end) is str:
      end_bytes = end.encode("cp932")
    else:
      end_bytes = end

    start_index = binary.find(start_bytes, start_index)
    if start_index == -1:
      return start_index
    index = start_index
    item = None
    while index < len(binary):
      zero_index = binary.find(b"\0", index)
      if zero_index == -1:
        break
      sub_bytes = binary[index:zero_index]
      if index != zero_index:
        if index > start_index and item:
          item["length"] = index - item["offset"] - 1
        item = {
          "speaker": "",
          "content": sub_bytes.decode("cp932"),
          "offset": index,
          "length": zero_index - index,
        }
        item["trash"] = TRASH_PATTERN.search(item["content"]) is not None
        output[f"offset_{index:08x}"] = item

      index = zero_index + 1
      if sub_bytes == end_bytes:
        break

    return index

  with open(input_path, "rb") as reader:
    binary = reader.read()

  output = {}
  index = 0
  for start, end in hardcoded_texts:
    index = find_strings(binary, output, start, end, index)
    if index == -1:
      break

  output_path = f"{message_root}/{sheet_name}.json"
  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  with open(output_path, "w", -1, "utf8") as writer:
    json.dump(output, writer, ensure_ascii=False, indent=2)


if __name__ == "__main__":
  export_arm9(
    ARM9_DECOMPRESSED_PATH,
    "arm9.bin",
    f"{DIR_TEMP_JSON}/ja",
    HARDCODED_TEXTS_ARM9_BIN,
  )
