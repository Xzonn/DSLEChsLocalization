import os
import re
import shutil
import struct
import subprocess

from helper import (
  DIR_ARM9_PATCH,
  DIR_ORIGINAL_FILES,
  DIR_TEMP_DECOMPRESSED,
  DIR_TEMP_DECOMPRESSED_MODIFIED,
  SYMBOL_OUT_PATH,
)

SYMBOL_PATTERN = re.compile(r"^(?P<address>[0-9a-f]{8}) .+\.text\t[0-9a-f]{8} (?P<name>[^\.].+)$", re.MULTILINE)


def compile_helper(
  root: str, folder_name: str, binary: bytes, symbols: list[tuple[str, int]], ram_offset: int = 0x2000000
) -> bytes:
  for folder in os.listdir(f"{root}/{folder_name}"):
    if not os.path.isdir(f"{root}/{folder_name}/{folder}"):
      continue

    address = int(folder, 16)
    p = subprocess.run(
      [
        "make",
        f"TARGET=repl_{address:07X}",
        f"SOURCES={folder_name}/{folder}",
        f"CODEADDR=0x{address:07X}",
      ],
      cwd=root,
    )
    if p.returncode != 0:
      raise Exception(f"Failed to compile {folder}")

    with open(f"{root}/repl_{address:07X}.bin", "rb") as reader:
      patch = reader.read()

    binary = binary[: address - ram_offset] + patch + binary[address - ram_offset + len(patch) :]

    with open(f"{root}/repl_{address:07X}.sym", "r", -1, "utf8") as reader:
      symbols_text = reader.read()

    for result in SYMBOL_PATTERN.finditer(symbols_text):
      symbols.append((result.group("name"), int(result.group("address"), 16)))

  return binary


def compile_arm9_patch(
  root: str,
  arm9_path: str,
  overarm9_path: str,
  arm9_output_path: str,
  symbol_output_path: str,
):
  if os.path.exists(f"{root}/build"):
    shutil.rmtree(f"{root}/build")
  for file_name in os.listdir(root):
    if file_name.startswith("repl_"):
      os.remove(f"{root}/{file_name}")

  symbols = []

  input_path = f"{arm9_path}/arm9.bin"
  if os.path.exists(f"{arm9_output_path}/arm9.bin"):
    input_path = f"{arm9_output_path}/arm9.bin"
  with open(input_path, "rb") as reader:
    arm9 = reader.read()

  arm9 = compile_helper(root, "src", arm9, symbols)

  os.makedirs(arm9_output_path, exist_ok=True)
  with open(f"{arm9_output_path}/arm9.bin", "wb") as writer:
    writer.write(arm9)

  overlay_addresses = []
  with open(overarm9_path, "rb") as reader:
    while True:
      buffer = reader.read(0x20)
      if not buffer:
        break
      index, ram_address = struct.unpack("<II", buffer[:8])
      overlay_addresses.append(ram_address)

  for file_name in os.listdir(f"{arm9_path}/overlay"):
    overlay_name = file_name.removesuffix(".bin")
    if not os.path.isdir(f"{root}/{overlay_name}"):
      continue
    index = int(overlay_name.removeprefix("overlay_"))

    input_path = f"{arm9_path}/overlay/{file_name}"
    if os.path.exists(f"{arm9_output_path}/overlay/{file_name}"):
      input_path = f"{arm9_output_path}/overlay/{file_name}"
    with open(input_path, "rb") as reader:
      overlay = reader.read()

    overlay = compile_helper(root, overlay_name, overlay, symbols, overlay_addresses[index])

    os.makedirs(f"{arm9_output_path}/overlay", exist_ok=True)
    with open(f"{arm9_output_path}/overlay/{file_name}", "wb") as writer:
      writer.write(overlay)

  with open(symbol_output_path, "w", -1, "utf8", None, "\n") as writer:
    for name, address in sorted(symbols, key=lambda x: x[1]):
      writer.write(f"{name} = 0x{address:08X};\n")


if __name__ == "__main__":
  compile_arm9_patch(
    DIR_ARM9_PATCH,
    DIR_TEMP_DECOMPRESSED,
    f"{DIR_ORIGINAL_FILES}/overarm9.bin",
    DIR_TEMP_DECOMPRESSED_MODIFIED,
    SYMBOL_OUT_PATH,
  )
