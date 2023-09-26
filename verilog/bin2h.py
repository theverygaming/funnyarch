import sys

with open("output.bin", "rb") as f:
    data = f.read()

if len(data) % 4 != 0:
    print("appending zeros to file for alignment", file=sys.stderr)
    n = 4 - (len(data) % 4)
    data = bytearray(data)
    for _ in range(n):
        data.append(0)

for i in range(int(len(data) / 4)):
    arr = data[(i * 4) : (i * 4) + 4]
    print(f"{arr[3]:02x}{arr[2]:02x}{arr[1]:02x}{arr[0]:02x}")
