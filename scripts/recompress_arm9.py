import os
import struct

import ndspy.codeCompression
from helper import ARM9_MODIFIED_PATH, ARM9_OUT_PATH, ARM9_PATH


def decompress_arm9(original_path: str, modified_path: str, output_path: str):
  with open(original_path, "rb") as reader:
    compressed = reader.read()
  nitro_code = compressed[-12:]
  with open(modified_path, "rb") as reader:
    decompressed = reader.read()
  compressed = bytearray(ndspy.codeCompression.compress(decompressed, True))
  compressed[0x0B9C : 0x0B9C + 4] = struct.pack("<I", 0x2000000 + len(compressed))

  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  with open(output_path, "wb") as writer:
    writer.write(compressed + nitro_code)


if __name__ == "__main__":
  decompress_arm9(ARM9_PATH, ARM9_MODIFIED_PATH, ARM9_OUT_PATH)
