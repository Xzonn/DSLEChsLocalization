$nitropacker = "bin\NitroPacker\HaroohieClub.NitroPacker.Cli\bin\Release\net8.0\publish\NitroPacker.exe"

# Clean output folder
if (Test-Path -Path "out\" -PathType "Container") {
  Remove-Item -Recurse -Force "out\"
}
if (Test-Path -Path "temp\" -PathType "Container") {
  Remove-Item -Recurse -Force "temp\"
}

# Prepare for tools
dotnet publish -c Release --framework "net8.0" "bin\NitroPacker\HaroohieClub.NitroPacker.Cli\HaroohieClub.NitroPacker.Cli.csproj"

# Unpack/extract original files
python scripts\unpack_pak.py
python scripts\decompress_arm9.py
python scripts\export_arm9.py
python scripts\convert_messages_to_json.py

& $nitropacker "patch-arm9" -i "src" -o "temp/nitro" -a "02006514"

python scripts\generate_char_table.py

python scripts\import_csv_to_json.py
python scripts\convert_json_to_messages.py

python scripts\create_font.py

python scripts\convert_png_to_bg.py

python scripts\import_arm9.py
python scripts\recompress_arm9.py
python scripts\repack_pak.py

python scripts\edit_banner.py

Compress-Archive -Path "out/data/", "out/arm9.bin", "out/banner.bin" -Destination "patch-ds.zip" -Force
Move-Item -Path "patch-ds.zip" -Destination "out/patch-ds.xzp" -Force
