import os
import shutil

from helper import (
  DIR_IMAGES_SPR_FILES,
  DIR_SPR_NCER,
  DIR_SPR_NCGR,
  DIR_TEMP_IMPORT,
)

SPR_COUNT = 0x0BD1

os.makedirs(f"{DIR_TEMP_IMPORT}/{DIR_SPR_NCER}", exist_ok=True)
os.makedirs(f"{DIR_TEMP_IMPORT}/{DIR_SPR_NCGR}", exist_ok=True)

for i in range(SPR_COUNT):
  ncer_path = f"{DIR_IMAGES_SPR_FILES}/{i:04d}.ncer"
  ncgr_path = f"{DIR_IMAGES_SPR_FILES}/{i:04d}.ncgr"

  if not os.path.exists(ncer_path) or not os.path.exists(ncgr_path):
    continue

  shutil.copy(ncer_path, f"{DIR_TEMP_IMPORT}/{DIR_SPR_NCER}/{i:04d}.bin")
  shutil.copy(ncgr_path, f"{DIR_TEMP_IMPORT}/{DIR_SPR_NCGR}/{i:04d}.bin")
