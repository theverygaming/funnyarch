with open("output.bin", "rb") as f:
    data = f.read()

i = 0
for byte in data:
    print(f"mem[{i}] = 8'h{byte:x};")
    i += 1
