import os
import struct
from helper import DIR_TEMP_IMPORT, DIR_ORIGINAL_FILES, DIR_OUT


def repack_pak(original_path: str, input_path: str, output_path: str):
  input_folder = os.path.splitext(input_path)[0]
  if not os.path.exists(input_folder):
    return

  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  reader = open(original_path, "rb")
  writer = open(output_path, "wb")
  file_count, version = struct.unpack("<I12s", reader.read(0x10))
  writer.write(struct.pack("<I12s", file_count, version))
  pos = 0x10 + 0x10 * file_count

  for i in range(file_count):
    start, size1, size2, flags = struct.unpack("<4I", reader.read(0x10))
    writer.seek(0x10 + 0x10 * i)
    if os.path.exists(f"{input_folder}/{i:04d}.bin"):
      size = os.path.getsize(f"{input_folder}/{i:04d}.bin")
      writer.write(struct.pack("<4I", pos, size, size, 0x80000000))
      writer.seek(pos)
      with open(f"{input_folder}/{i:04d}.bin", "rb") as reader2:
        writer.write(reader2.read())
      pos += size
    else:
      reader_pos = reader.tell()
      writer.write(struct.pack("<4I", pos, size1, size2, flags))
      writer.seek(pos)
      reader.seek(start)
      writer.write(reader.read(size2))
      reader.seek(reader_pos)
      pos += size2


def repack_pak_in_folder(original_files_root: str, input_files_root: str, output_root: str):
  for root, dirs, files in os.walk(original_files_root):
    for file_name in files:
      if file_name.lower().endswith(".pak"):
        relative_path = os.path.relpath(root, original_files_root)
        repack_pak(
          f"{root}/{file_name}",
          f"{input_files_root}/{relative_path}/{file_name}",
          f"{output_root}/{relative_path}/{file_name}",
        )


if __name__ == "__main__":
  repack_pak_in_folder(DIR_ORIGINAL_FILES, DIR_TEMP_IMPORT, DIR_OUT)
