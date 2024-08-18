import ndspy.codeCompression
from helper import ARM9_DECOMPRESSED_PATH, ARM9_PATH


def decompress_arm9(original_path: str, output_path: str):
  with open(original_path, "rb") as reader:
    compressed = reader.read()
  decompressed = ndspy.codeCompression.decompress(compressed[:-12])

  with open(output_path, "wb") as writer:
    writer.write(decompressed)


if __name__ == "__main__":
  decompress_arm9(ARM9_PATH, ARM9_DECOMPRESSED_PATH)
