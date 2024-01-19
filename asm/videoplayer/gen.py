import sys
from enum import Enum
import numpy as np
from wand.image import Image as WandImage
import cv2

def write_le_file(file, bytes, num):
    num &= (1 << (bytes * 8)) - 1
    file.write(num.to_bytes(bytes, "little"))

def dither(image):
    img = WandImage.from_array(image, channel_map="I")
    img.ordered_dither('4x4')

    img_buffer = np.frombuffer(img.make_blob(format="gray"))

    img_buffer=np.asarray(bytearray(img.make_blob('bmp')), dtype=np.uint8)
    outimg = cv2.imdecode(img_buffer, cv2.IMREAD_UNCHANGED)
    outimg = cv2.cvtColor(outimg, cv2.COLOR_BGR2GRAY)
    return outimg

# https://stackoverflow.com/a/32681075
def rle(inarray):
        """ run length encoding. Partial credit to R rle function. 
            Multi datatype arrays catered for including non Numpy
            returns: Array[tuple (start, length, value)]"""
        ia = np.asarray(inarray)                # force numpy
        n = len(ia)
        if n == 0: 
            return []
        else:
            y = ia[1:] != ia[:-1]               # pairwise unequal (string safe)
            i = np.append(np.where(y), n - 1)   # must include last element posi
            z = np.diff(np.append(-1, i))       # run lengths
            p = np.cumsum(np.append(0, z))[:-1] # positions
            return list(zip(p, z, ia[i]))

class FrameType(Enum):
    RUNLENGTH = 1
    BITMAP = 2

if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} input output")
    exit(1)

try:
    video = cv2.VideoCapture(sys.argv[1])
    assert video.isOpened()
except Exception as e:
    print(f"error: opening input file {e}")
    exit(1)

outfile = open(sys.argv[2], "w+b")

decodedframe = None
prev_frame = None
while True:
    ret, frame = video.read()
    if not ret:
        break
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
    frame = dither(frame)

    frame_enc = frame.copy()
    if prev_frame is not None:
        diff = prev_frame == frame_enc
        # set each pixel that has not changed to 4
        frame_enc[diff] = 4
    prev_frame = frame
    runlength = rle(np.reshape(frame_enc, (frame_enc.shape[0]*frame_enc.shape[1]))) # (start, length, value)
    # filter out all unchanged pixels (they were set to 4)
    runlength = list(filter(lambda f: f[2] != 4, runlength))
    runlength = [(int(s), int(l), v == 255) for s, l, v in runlength] # (start, length, white)

    # frames = []
    
    # bitmapThreshold = 32

    # i = 0
    # nbmp_frm = 0
    # nbmp_bits = 0
    # while i < len(runlength):
    #     if i < len(runlength):
    #         nbmp = 0
    #         j = 1
    #         while (i+j) < len(runlength): # should be a while loop
    #             if ((runlength[i+j][0]+runlength[i+j][1]) - runlength[i][0]) > bitmapThreshold:
    #                 break
    #             nbmp += 1
    #             nbmp_bits += runlength[i+j][1]

    #             j += 1
    #         if nbmp > 0:
    #             #print(f"bitmap candidates {nbmp}")
    #             i += nbmp
    #             nbmp_frm += nbmp
    #             continue
    #     frames.append((FrameType.RUNLENGTH, runlength[i]))
    #     i += 1
    # print(f"    frame bitmap candidates {nbmp_frm}... {nbmp_bits/8} bytes")

    # runlength = list(filter(lambda f: f[1] > 1, runlength))
    # print(f"    -> reduced frame count to {len(runlength)}")



    if decodedframe is None:
        decodedframe = np.zeros(frame.shape, dtype="uint8")
    decodedframe = np.reshape(decodedframe, (frame.shape[0]*frame.shape[1]))
    for soffset, npixels, white in runlength:
        decodedframe[soffset:soffset+(npixels)] = 255 if white else 0
    decodedframe = np.reshape(decodedframe, frame.shape)

    write_le_file(outfile, 4, 0)
    write_le_file(outfile, 4, 0)
    for soffset, npixels, white in runlength:
        num = 0x01
        num |= (soffset & 0x7FFFF) << 8
        num |= (1 if white else 0) << 27
        num |= (npixels & 0x7FFFF) << 32
        write_le_file(outfile, 4, num)
        write_le_file(outfile, 4, num >> 32)

    cv2.imshow("image", np.concatenate((frame, decodedframe), axis=1))

    if cv2.waitKey(1) == ord("q"):
        break

# end command
write_le_file(outfile, 4, 0x02)
write_le_file(outfile, 4, 0)

outfile.close()
video.release()
