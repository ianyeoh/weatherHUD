#!/usr/bin/env python
import sys
import os


# Python script converting a PBM image into a byte array
# that can be used to construct a MicroPython framebuffer
def main():
    if len(sys.argv) != 2:
        usage()
        return 2

    with open(sys.argv[1], 'rb') as fd:
        pbm_format = fd.readline().strip()
        if pbm_format != b'P4':
            print("ERROR: input file must be binary PBM (type P4)",
                  file = sys.stderr)
            return 1
        _ = fd.readline() # ignore a comment which is added when exporting .pbm files in GIMP
        pbm_dims = [int(d) for d in fd.readline().strip().split()]
        pbm_data = fd.read()

    fbbase = "fb_{0}".format(os.path.basename(sys.argv[1]))
    fbname = os.path.splitext(fbbase)[0]
    with sys.stdout as fd:
        f = "{0} = framebuf.FrameBuffer(bytearray({1}), {2}, {3}, framebuf.MONO_HLSB)\n"
        fd.write(f.format(fbname, str(pbm_data), pbm_dims[0], pbm_dims[1]))


def usage():
    print("""usage: {0} PBM_FILE""".format(os.path.basename(sys.argv[0])),
          file = sys.stderr)

if __name__ == '__main__':
    main()