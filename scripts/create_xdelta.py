import logging
import os
import zlib

import pyxdelta
from helper import DIR_ORIGINAL_FILES, DIR_OUT, DIR_TEMP_OUT


def create_xdelta(original_root: str, modified_root: str, output_root: str):
  for root, dirs, files in os.walk(modified_root):
    for file in files:
      modified_file_path = f"{root}/{file}"
      rel_file_path = os.path.relpath(f"{root}/{file}", modified_root)
      original_file_path = f"{original_root}/{rel_file_path}"

      if not os.path.exists(original_file_path):
        logging.warning(f"Original file not found: {original_file_path}")
        continue

      if os.path.getsize(original_file_path) == os.path.getsize(modified_file_path):
        original_crc_32 = zlib.crc32(open(original_file_path, "rb").read())
        modified_crc_32 = zlib.crc32(open(modified_file_path, "rb").read())
        if original_crc_32 == modified_crc_32:
          continue

      output_path = f"{output_root}/xdelta/{rel_file_path}"
      os.makedirs(os.path.dirname(output_path), exist_ok=True)
      pyxdelta.run(original_file_path, modified_file_path, output_path)


if __name__ == "__main__":
  create_xdelta(DIR_ORIGINAL_FILES, DIR_TEMP_OUT, DIR_OUT)
