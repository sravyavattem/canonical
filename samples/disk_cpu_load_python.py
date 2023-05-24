#!/usr/bin/env python3
# Script to test CPU load imposed by a simple disk read operation

# Parameters:
#  --max-load (int) -- The maximum acceptable CPU load, as a percentage.
#                       Defaults to 30.
#  --xfer (int) -- The amount of data to read from the disk, in
#                        mebibytes. Defaults to 4096 (4 GiB).
#  --verbose -- If present, produce more verbose output
#  <device-filename> -- This is the WHOLE-DISK device filename


import argparse
import subprocess
import os

def get_params():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Define command line arguments
    parser.add_argument("--max-load", type=int, default=30)
    parser.add_argument("--xfer", type=int, default=4096)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("device_filename", nargs='?', default="/dev/sda")

    # Parse command line arguments
    args = parser.parse_args()

    # Return parsed arguments
    return args


def sum_array(arr):
    # Calculate sum of the array
    total = sum(arr)
    return total


def compute_cpu_load(start_use, end_use, verbose):
    # Remove the lines that start with "cpu"
    print(start_use)
    start_use = [value for value in start_use if not value.startswith("cpu")]
    end_use = [value for value in end_use if not value.startswith("cpu")]

    # Convert the values from strings to integers
    start_use = [int(value) for value in start_use]
    end_use = [int(value) for value in end_use]

    #compute the difference
    diff_idle = end_use[3] - start_use[3]
    start_total = sum_array(start_use)
    end_total = sum_array(end_use)
    diff_total = end_total - start_total
    diff_used = diff_total - diff_idle

    if verbose:
        print("Start CPU time =", start_total)
        print("End CPU time =", end_total)
        print("CPU time used =", diff_used)
        print("Total elapsed time =", diff_total)

    if diff_total != 0:
        cpu_load = (diff_used * 100) // diff_total
    else:
        cpu_load = 0

    # Return the computed CPU load
    return cpu_load


# Main program body
if __name__ == '__main__':
    # Parse the command line arguments
    args = get_params()

    retval = 0
    print(f"Testing CPU load when reading {args.xfer} MiB from {args.device_filename}")
    print(f"Maximum acceptable CPU load is {args.max_load}")
    
    # Flush buffers for the disk device
    subprocess.run(["blockdev", "--flushbufs", args.device_filename])

    # Get CPU statistics at the start
    start_load = subprocess.check_output(["grep", "cpu", "/proc/stat"]).decode().split()[1:]

    if args.verbose:
        print("Beginning disk read....")

    # Perform disk read using dd command
    subprocess.run(["dd", "if=" + args.device_filename, "of=/dev/null", "bs=1048576", "count=" + str(args.xfer)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if args.verbose:
        print("Disk read complete!")

    # Get CPU statistics at the end
    end_load = subprocess.check_output(["grep", "cpu", "/proc/stat"]).decode().split()[1:]

    # Compute CPU load
    cpu_load = compute_cpu_load(start_load, end_load, args.verbose)
    print("Detected disk read CPU load is", cpu_load)

    if cpu_load > args.max_load:
        retval = 1
        print("*** DISK CPU LOAD TEST HAS FAILED! ***")

    # Exit with the return value
    exit(retval)