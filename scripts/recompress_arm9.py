import os
import struct

import ndspy.codeCompression
from helper import (
  ARM9_COMPRESSED_SIZE_OFFSET,
  DIR_ORIGINAL_FILES,
  DIR_TEMP_DECOMPRESSED_MODIFIED,
  DIR_TEMP_OUT,
)


def decompress_arm9(original_root: str, modified_root: str, output_root: str):
  with open(f"{original_root}/arm9.bin", "rb") as reader:
    compressed = reader.read()
  nitro_code = compressed[-12:]
  with open(f"{modified_root}/arm9.bin", "rb") as reader:
    decompressed = reader.read()
  compressed = bytearray(ndspy.codeCompression.compress(decompressed, True))
  compressed[ARM9_COMPRESSED_SIZE_OFFSET : ARM9_COMPRESSED_SIZE_OFFSET + 4] = struct.pack(
    "<I", 0x2000000 + len(compressed)
  )

  os.makedirs(output_root, exist_ok=True)
  with open(f"{output_root}/arm9.bin", "wb") as writer:
    writer.write(compressed + nitro_code)

  if not os.path.exists(f"{modified_root}/overlay"):
    return

  for file_name in os.listdir(f"{modified_root}/overlay"):
    with open(f"{modified_root}/overlay/{file_name}", "rb") as reader:
      decompressed = reader.read()
    compressed = bytearray(ndspy.codeCompression.compress(decompressed, False))

    output_path = f"{output_root}/overlay/{file_name}"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as writer:
      writer.write(compressed)


if __name__ == "__main__":
  decompress_arm9(DIR_ORIGINAL_FILES, DIR_TEMP_DECOMPRESSED_MODIFIED, DIR_TEMP_OUT)
