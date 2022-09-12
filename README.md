# DJI FPV Altitude Telemetry Fix

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

## Example

My drone recorded a single flight in two separate video files, and
recorded the telemetry data in two corresponding SRT files.

```
DJI_0015.MP4
DJI_0016.MP4

DJI_0015.SRT
DJI_0016.SRT
```

Steps to fix SRT data:
In this example, the starting altitude in the first SRT file is `-8.398028`.

1. Run the utility: `python3 fixalt.py DJI_0015.SRT DJI_0016.SRT`. It will
   detect the starting altitude, and adjust the entire data set up or down until
   the starting altitude is 0.00.
2. This would shift and correct the files and save them to `DJI_0015_CORRECTED.SRT` and
   `DJI_0016_CORRECTED.SRT`.
3. If you want to manually specify the altitude shift amount, open the first
   SRT file (`DJI_0015.SRT`) with a text editor and inspect the first record.
   You will see the starting altitude listed as `altitude: -8.398028`. You would
   therefore specify the shift amount as 8.398028 in order to to set the
   starting altitude of the flight to 0.00.
   `python3 fixalt.py --shift 8.398028 DJI_0015.SRT DJI_0016.SRT`.

## Installation

1. Install Python >=3.6. This can be installed through the Windows store if on
Windows, and should be available by default on Linux.

## Usage

1. Copy your original SRT files into the script directory.
2. Run the script. `python3 fixalt.py <file1> <file2> <file3>` where `file1`
is the first file in a single drone flight. Files 2..n are additional SRT files
from the same drone flight.

The tool will automatically detect starting altitude from a flight and will adjust
the SRT files to be where the starting altitude of the flight is 0.00. You can
also adjust the altitude shift manually if you want by specifying the `--shift`
command line option.
