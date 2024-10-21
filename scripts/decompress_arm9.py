import os

import ndspy.codeCompression
from helper import DIR_ORIGINAL_FILES, DIR_TEMP_DECOMPRESSED


def decompress_arm9(original_root: str, output_root: str):
  with open(f"{original_root}/arm9.bin", "rb") as reader:
    compressed = reader.read()
  decompressed = ndspy.codeCompression.decompress(compressed[:-12])

  os.makedirs(output_root, exist_ok=True)
  with open(f"{output_root}/arm9.bin", "wb") as writer:
    writer.write(decompressed)

  if not os.path.exists(f"{original_root}/overlay"):
    return

  for file_name in os.listdir(f"{original_root}/overlay"):
    with open(f"{original_root}/overlay/{file_name}", "rb") as reader:
      compressed = reader.read()
    decompressed = ndspy.codeCompression.decompress(compressed)

    output_path = f"{output_root}/overlay/{file_name}"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as writer:
      writer.write(decompressed)


if __name__ == "__main__":
  decompress_arm9(DIR_ORIGINAL_FILES, DIR_TEMP_DECOMPRESSED)
