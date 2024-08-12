@ 另外一处排序，将保存的数据修改为了全名的指针，R0-R1 现在为 byte**。
@ 注意 R0-R1 可能不是按 4 字节对齐的，因此需要分别取高字节和低字节拼接。

repl_020CABAC:
  LDRH R2, [R0]
  LDRH R0, [R0, #2]
  ADD R0, R2, R0, LSL#16
  LDRH R2, [R1]
  LDRH R1, [R1, #2]
  ADD R1, R2, R1, LSL#16
  B compare_digimon_name_new
