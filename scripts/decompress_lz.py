def decompress_lz(input_data: bytes, decompressed_size: int) -> bytes:
  output = bytearray(decompressed_size)
  temp = bytearray(0x1000)
  output_pos = 0
  input_pos = 4

  while input_pos < len(input_data):
    bits = input_data[input_pos]
    input_pos += 1

    for bit in range(8):
      if (bits & 1) == 1:
        b = input_data[input_pos]
        input_pos += 1
        temp[output_pos % 0x1000] = b
        output[output_pos] = b
        output_pos += 1
      else:
        if input_pos + 1 >= len(input_data):
          break
        low = input_data[input_pos]
        high = input_data[input_pos + 1]
        input_pos += 2

        max_length = (high & 0x0F) + 2
        start_pos = low | ((high & 0xF0) << 4)

        for i in range(max_length + 1):
          b = temp[(start_pos + i + 0x12) % 0x1000]
          temp[output_pos % 0x1000] = b
          output[output_pos] = b
          output_pos += 1

      bits >>= 1

  return bytes(output)
