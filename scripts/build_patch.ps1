# Clean output folder
if (Test-Path -Path "out\" -PathType "Container") {
  Remove-Item -Recurse -Force "out\"
}
if (Test-Path -Path "temp\" -PathType "Container") {
  Remove-Item -Recurse -Force "temp\"
}

# Unpack/extract original files
if (-Not (Test-Path -Path "unpacked\data\FONT_NFTR\0000.bin" -PathType "Leaf")) {
  if (Test-Path -Path "unpacked\" -PathType "Container") {
    Remove-Item -Recurse -Force "unpacked\"
  }
  python scripts\unpack_pak.py
}
python scripts\decompress_arm9.py

python scripts\generate_char_table.py
python scripts\create_font.py

python scripts\convert_json_to_messages.py
python scripts\convert_json_to_binary.py

python scripts\convert_png_to_bg.py
python scripts\convert_png_to_spr.py

python scripts\repack_pak.py

python scripts\compile_arm9_patch.py
python scripts\recompress_arm9.py
python scripts\create_xdelta.py

python scripts\edit_banner.py

New-Item -ItemType Directory -Path "out\data\" -Force | Out-Null
Copy-Item -Path "files\dwc\" -Destination "out\data\" -Recurse -Force

Compress-Archive -Path "out/data", "out/xdelta/", "out/banner.bin" -Destination "patch-ds.zip" -Force
Move-Item -Path "patch-ds.zip" -Destination "out/patch-ds.xzp" -Force
