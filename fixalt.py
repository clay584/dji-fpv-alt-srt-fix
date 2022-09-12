#!/usr/bin/env python
import sys
import re
import argparse

EPILOG = """DJI FPV Altitude Telemetry Fix

As of 9/12/2022 the DJI FPV drone displays altitude correctly
in the goggles, but when it writes to the telemtry file (SRT),
it does not write the correct values. This tool will correct
the telemetry files.

Specifically, there are two issues that are addressed:

1) The starting altitude is often incorrect. For example,
   when the recording starts, and the drone is on the ground,
   the altitude will show a non-zero number in the SRT file.
2) The values written to the SRT file for altitude appear to
   be 1/10 of the actual altutude of the drone (likely
   firmware bug in the drone).

To fix #1, you the user, must specify the amount to shift the altitude
readings. That value will then shift up or down the entire set of
data in the SRT files. If you do not specify a shift amount, the tool
will detect the starting altitude and shift the entire flight to a
starting altitude of 0.00.

To fix #2, this utility will multiply the shifted values by 10.

Example:

My drone recorded a single flight in two separate video files, and
recorded the telemetry data in two corresponding SRT files.

DJI_0015.MP4
DJI_0016.MP4

DJI_0015.SRT
DJI_0016.SRT

Steps to fix SRT data:
In this example, the starting altitude in the first SRT file is -8.398028.

1) Run the utility: 'python3 fixalt.py DJI_0015.SRT DJI_0016.SRT'. It will
   detect the starting altitude, and adjust the entire data set up or down until
   the starting altitude is 0.00.

2) This would shift and correct the files and save them to 'DJI_0015_CORRECTED.SRT and
   DJI_0016_CORRECTED.SRT'.

3) If you want to manually specify the altitude shift amount, open the first
   SRT file (DJI_0015.SRT) with a text editor and inspect the first record.
   You will see the starting altitude listed as 'altitude: -8.398028'. You would
   therefore specify the shift amount as 8.398028 in order to to set the
   starting altitude of the flight to 0.00.
   'python3 fixalt.py --shift 8.398028 DJI_0015.SRT DJI_0016.SRT'.

"""


class Reading:
    def __init__(self, raw, shift=0):
        self.raw = raw
        self.shift = shift
        self.original_alt = self.get_original_alt()
        self.corrected_alt = self.correct_alt()
        self.corrected_raw = self.generate_correct_raw()

    def get_original_alt(self):
        result = re.search("\[altitude: (.+)\]", self.raw)
        return float(result[1])

    def correct_alt(self):
        # Shift altitudes
        shifted = self.original_alt - self.shift

        # Correct altitudes
        return shifted * 10

    def generate_correct_raw(self):
        return re.sub(
            r"\[altitude: (.+)\]",
            str(f"[altitude: {format(self.corrected_alt, '.6f')}]"),
            self.raw,
        )


class SRT:
    def __init__(self, filename, shift=0):
        self.filename = filename
        with open(self.filename, "r") as f:
            self.raw = f.read()

        self.text_items = self.raw.split("\n\n")
        self.text_items.pop(-1)
        # Cannot assume that the start of the video is sitting on ground
        # self.shift = Reading(self.text_items[0]).original_alt
        self.shift = shift
        self.readings = [Reading(x, self.shift) for x in self.text_items]
        self.out_file = self.gen_output_name()
        self.write_out()

    def gen_output_name(self):
        filename_base = ".".join(self.filename.split(".")[:-1])
        file_ext = self.filename.split(".")[-1:][0]
        return f"{filename_base}_CORRECTED.{file_ext}"

    def write_out(self):
        with open(self.out_file, "w") as f:
            for i in self.readings:
                f.write(f"{i.corrected_raw}\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Utility for fixing DJI FPV Telemetry Files",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--shift", dest="shift", help="Altitude Shift Amount")
    parser.add_argument("files", nargs="*", help="One or more files to process")
    args = parser.parse_args()

    # If user did not specify shift amount, detect
    if args.shift is None:
        for i in args.files:
            srt = SRT(i, shift=0)
            starting_alt = srt.readings[0].original_alt
            shift = starting_alt
            print(
                f"No altitude shift amount provided, detected starting altitude of {'{:+f}'.format(float(shift))}"
            )
            print(f"Data set will be shifted by {'{:+f}'.format(0 - float(shift))}")
            break
    else:
        shift = 0 - float(args.shift)
        print(f"Altitude shift amount provided: {'{:+f}'.format(float(args.shift))}")
        print(f"Data set will be shifted by {'{:+f}'.format(float(args.shift))}")

    if len(args.files) == 0:
        print(
            "You must specify at least one SRT file. Type --help for usage. Exiting..."
        )
        sys.exit(1)
    for i in args.files:
        print(f"Analyzing {i}")
        srt = SRT(i, shift=float(shift))
        print(f"Wrote output file to {srt.out_file}")
