#include "nds/ndstypes.h"

extern u16 NNSi_G2dSplitCharShiftJIS(u8 **src);

// 原本的排序功能调用了 02140A0C-02140BF0 范围内保存的数据，这部分数据是 Shift-JIS 编码的平片假名和英文字母，用于排序。
// 为了按拼音排序，已经将码表替换为了拼音顺序，因此只需要让排序函数对字符码位排序即可。

int32 compare_digimon_name_new(u8 *a, u8 *b)
{
  u8 **a_loc = &a;
  u8 **b_loc = &b;
  u16 a_char = NNSi_G2dSplitCharShiftJIS(a_loc);
  u16 b_char = NNSi_G2dSplitCharShiftJIS(b_loc);
  while (a_char == b_char)
  {
    if (a_char == 0)
    {
      return 0;
    }
    a_char = NNSi_G2dSplitCharShiftJIS(a_loc);
    b_char = NNSi_G2dSplitCharShiftJIS(b_loc);
  }
  if (a_char < b_char)
  {
    return -1;
  }
  return 1;
}
