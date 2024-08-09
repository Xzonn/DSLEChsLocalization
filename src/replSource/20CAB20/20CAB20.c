#include "nds/ndstypes.h"

// 重写比较函数。

int32 compare_digimon_name_new(u8* a, u8* b) {
  u32 i;
  for (i = 0; ; i += 2) {
    if ((a[i] == b[i]) && (a[i + 1] == b[i + 1])) {
      if (a[i] == 0) {
        return 0;
      }
      continue;
    }
    if ((a[i] < b[i]) || ((a[i] == b[i]) && (a[i + 1] < b[i + 1]))) {
      return -1;
    }
    return 1;
  }
}