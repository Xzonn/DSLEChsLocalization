import json
import os

from helper import DIR_TEXT_FILES, DIR_TEMP_JSON, convert_zh_hans_to_shift_jis, load_translations

LANGUAGE = os.getenv("XZ_LANGUAGE") or "zh_Hans"


def import_csv_to_json(csv_root: str, json_input_root: str, json_output_root: str):
  for root, dirs, files in os.walk(csv_root):
    for file_name in files:
      if not file_name.endswith(".json"):
        continue

      sheet_name = os.path.relpath(f"{root}/{file_name}", csv_root).replace("\\", "/").removesuffix(".json")
      json_path = f"{json_input_root}/{sheet_name}.json"
      if not os.path.exists(json_path):
        continue

      translations = load_translations(f"{root}/{file_name}")

      with open(json_path, "r", -1, "utf8") as reader:
        json_input = json.load(reader)

      for k, v in json_input.items():
        if v.get("trash", False):
          continue

        v["content"] = convert_zh_hans_to_shift_jis(translations.get(k, v["content"]))

      output_path = f"{json_output_root}/{sheet_name}.json"
      os.makedirs(os.path.dirname(output_path), exist_ok=True)
      with open(output_path, "w", -1, "utf8") as writer:
        json.dump(json_input, writer, ensure_ascii=False, indent=2)


if __name__ == "__main__":
  import_csv_to_json(f"{DIR_TEXT_FILES}/{LANGUAGE}", f"{DIR_TEMP_JSON}/ja", f"{DIR_TEMP_JSON}/{LANGUAGE}")
