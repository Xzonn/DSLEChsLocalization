import os
import struct
from helper import DIR_TEMP_IMPORT, DIR_ORIGINAL_FILES, DIR_OUT


def repack_pak(input_path: str, output_path: str):
  input_folder = os.path.splitext(input_path)[0]
  if not os.path.exists(input_folder):
    return

  file_list = sorted(filter(lambda x: x.endswith(".bin"), os.listdir(input_folder)), key=lambda x: int(x.split(".")[0]))
  file_count = len(file_list)

  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  writer = open(output_path, "wb")
  writer.write(struct.pack("<I12s", file_count, b"2.01\0\0\0\0\0\0\0\0"))
  pos = 0x10 + 0x10 * file_count
  for i, file_name in enumerate(file_list):
    writer.seek(0x10 + 0x10 * i)
    size = os.path.getsize(f"{input_folder}/{file_name}")
    writer.write(struct.pack("<4I", pos, size, size, 0x80000000))
    writer.seek(pos)
    with open(f"{input_folder}/{file_name}", "rb") as reader:
      writer.write(reader.read())
    pos += size


def repack_pak_in_folder(original_files_root: str, input_files_root: str, output_root: str):
  for root, dirs, files in os.walk(original_files_root):
    for file_name in files:
      if file_name.lower().endswith(".pak"):
        relative_path = os.path.relpath(root, original_files_root)
        repack_pak(
          f"{input_files_root}/{relative_path}/{file_name}",
          f"{output_root}/{relative_path}/{file_name}",
        )


if __name__ == "__main__":
  repack_pak_in_folder(DIR_ORIGINAL_FILES, DIR_TEMP_IMPORT, DIR_OUT)
