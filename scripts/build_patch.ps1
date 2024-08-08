# Clean output folder
if (Test-Path -Path "out\" -PathType "Container") {
  Remove-Item -Recurse -Force "out\"
}
if (Test-Path -Path "temp\" -PathType "Container") {
  Remove-Item -Recurse -Force "temp\"
}

# Unpack/extract original files
python scripts\unpack_pak.py
python scripts\convert_messages_to_json.py
python scripts\import_csv_to_json.py
python scripts\convert_json_to_messages.py
python scripts\create_font.py
python scripts\repack_pak.py

dotnet script scripts/edit_arm9.csx
dotnet script scripts/edit_banner.csx

Compress-Archive -Path "out/data/","out/arm9.bin","out/banner.bin" -Destination "patch-ds.zip" -Force
Move-Item -Path "patch-ds.zip" -Destination "out/patch-ds.xzp" -Force
