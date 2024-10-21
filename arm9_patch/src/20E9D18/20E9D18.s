@ 此处将全名的指针直接保存到 [R4] 中，同时修改 0x020CABAC 处的函数。
@ 注意 R4 可能不是按 4 字节对齐的，因此需要分别取高字节和低字节拼接。

repl_020E9D18:
  LDR R0, [SP, #0x20]
  SUB R0, R0, #2
  STRH R0, [R4]
  MOV R0, R0, LSR#0x10
  STRH R0, [R4, #2]
  B 0x20E9D58
