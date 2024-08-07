#!/usr/bin/env dotnet-script
#r "nuget: NitroHelper, 0.12.1"

var banner = new NitroHelper.Banner("original_files/banner.bin");
var title = "数码宝贝物语\n失落的进化\n万代南梦宫游戏";
banner.japaneseTitle = title;
banner.englishTitle = title;
banner.frenchTitle = title;
banner.germanTitle = title;
banner.italianTitle = title;
banner.spanishTitle = title;
banner.WriteTo("out/banner.bin");
Console.WriteLine("Banner saved.");