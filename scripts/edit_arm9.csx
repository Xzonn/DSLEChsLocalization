#!/usr/bin/env dotnet-script
#r "nuget: NitroHelper, 0.12.1"
#r "nuget: Xzonn.BlzHelper, 0.9.0"
using Xzonn.BlzHelper;

var arm9Comp = File.ReadAllBytes($"original_files/arm9.bin");
var nitroCode = arm9Comp.Skip(arm9Comp.Length - 12).ToArray();
var arm9 = BLZ.Decompress(arm9Comp.Take(arm9Comp.Length - 12).ToArray());

// ipfix
EditBinary(ref arm9, 0x440, "18 00 9F E5 00 10 90 E5 14 20 9F E5 02 00 51 E1 10 10 A0 03 0B 10 C0 05 B7 10 C0 05 1E FF 2F E1 64 41 26 02 2D DA 9F E1");
EditBinary(ref arm9, 0x9F8, "90 FE FF EA");

// Sort by char code
EditBinary(ref arm9, 0x0CAB18, "B0 00 D0 E1 0E F0 A0 E1");
EditBinary(ref arm9, 0x0CAB20, "00 20 A0 E1 00 30 A0 E3 30 40 2D E9 01 C0 80 E2 01 E0 81 E2 03 00 D2 E7 03 40 D1 E7 04 00 50 E1 07 00 00 1A 03 50 DC E7 03 40 DE E7 04 00 55 E1 05 00 00 1A 00 00 50 E3 30 80 BD 08 02 30 83 E2 F3 FF FF EA 07 00 00 3A 08 00 00 1A 01 30 83 E2 03 20 D2 E7 03 30 D1 E7 03 00 52 E1 00 00 E0 33 01 00 A0 23 30 80 BD E8 00 00 E0 E3 30 80 BD E8 01 00 A0 E3 30 80 BD E8");
EditBinary(ref arm9, 0x0CACC4, "00 F0 20 E3 00 F0 20 E3 93 FF FF EB");

// Hard-coded text width
EditBinary(ref arm9, 0x121D13, "09");
EditBinary(ref arm9, 0x12188C, "0A 05 04 09 0C 0C 0B 10");

var arm9New = arm9.Take(0x4000).Concat(BLZ.Compress(arm9.Skip(0x4000).ToArray())).Concat(nitroCode).ToArray();
uint newSize = (uint)(0x2000000 + arm9New.Length - 12);
Array.Copy(BitConverter.GetBytes(newSize), 0, arm9New, 0x0B9C, 4);

File.WriteAllBytes($"out/arm9.bin", arm9New);

void EditBinary(ref byte[] bytes, int offset, string newHexString)
{
  var newBytes = newHexString.Split(' ').Select(x => Convert.ToByte(x, 16)).ToArray();
  Array.Copy(newBytes, 0, bytes, offset, newBytes.Length);
  Console.WriteLine($"Edited binary at 0x{offset:X06} (length: 0x{newBytes.Length:X}): {newHexString}");
}