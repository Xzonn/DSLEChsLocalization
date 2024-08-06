import os
import struct
from helper import DIR_ORIGINAL_FILES, DIR_UNPACKED_FILES


def unpack_pak(input_path: str, output_path: str):
  reader = open(input_path, "rb")
  output_folder = os.path.splitext(output_path)[0]
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)

  file_count, version = struct.unpack("<I12s", reader.read(0x10))
  for i in range(file_count):
    start, size1, size2, flags = struct.unpack("<4I", reader.read(0x10))
    if flags & 0x80000000 != 0x80000000:
      print(f"Skipping {i:04d}.bin")
      continue
    assert size1 == size2
    pos = reader.tell()
    reader.seek(start)
    with open(f"{output_folder}/{i:04d}.bin", "wb") as writer:
      writer.write(reader.read(size1))
    reader.seek(pos)

  reader.close()


def unpack_pak_in_folder(original_files_root: str, unpacked_files_root: str):
  for root, dirs, files in os.walk(original_files_root):
    for file_name in files:
      if file_name.lower().endswith(".pak"):
        relative_path = os.path.relpath(root, original_files_root)
        unpack_pak(f"{root}/{file_name}", f"{unpacked_files_root}/{relative_path}/{file_name}")


if __name__ == "__main__":
  unpack_pak_in_folder(DIR_ORIGINAL_FILES, DIR_UNPACKED_FILES)
