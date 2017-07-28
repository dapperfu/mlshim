# -*- coding: utf-8 -*-
import os
from subprocess import Popen
import time

SLEEP_TIME = 5
START_TIMEOUT = 180
RUN_TIMEOUT = 7200

def matlab_run_wait(cmd_array, matlab_log=None):
    """
    Run the cmd_array with Popen, parse matlab_log for
        output from generate_run_script.

    Wait until matlab finishes to exit.

    Args:

        cmd_array (list)
            Output of ```mlrunner.matlab_cmd```

        matlab_log (str)
            Logfile to parse for status.

    Exceptions:
        TimeoutError("Logfile creation timed out")
        TimeoutError("Matlab start timed out")
        TimeoutError("Matlab execution timed out")
        Runtimeprint("Matlab processing failed")
    """
       
    # Remove log file if it exists.
    if os.path.exists(matlab_log):
        os.unlink(matlab_log)
    
    # Run the matlab command
    proc = Popen(cmd_array)
    # Start timer
    t_start = time.time()

    # Step 1. Wait for the log file to exist
    while not os.path.exists(matlab_log):
        # Check to see if timeout has been exceeded
        if time.time() - t_start > START_TIMEOUT:
            # Print the ERROR and raise a timeout ERROR
            print('{:.2f}s Timelimit Exceeded'.format(START_TIMEOUT))
            raise TimeoutError("Logfile creation timed out")
        print("Waiting for log to exist.")
        # Sleep to allow the process to run
        time.sleep(SLEEP_TIME)
    if not os.path.exists(matlab_log):
        print('Matlab start failed')
        # exit
    else:
        print("Logfile created in {:.2f}s".format(time.time() - t_start))
    # Step 2
    # Wait for Matlab to start and execute the script
    started = False
    while not started:
        # Read the log file
        with open(matlab_log, "r") as fid:
            lines = fid.readlines()
        # Read each of the lines in it and remove the new line endings.
        lines = [line.strip() for line in lines]
        # If we've found the "Started" string, matlab has made it that far into
        # the script.
        if "########## Started ##########" in lines:
            started = True
            continue
        # Check to see if timeout has been exceeded
        if time.time() - t_start > START_TIMEOUT:
            proc.kill()
            # Print the error and raise a timeout error
            print('{:.2f}s Timelimit Exceeded'.format(START_TIMEOUT))
            TimeoutError("Matlab start timed out")
        print("Waiting for Matlab to start.")
        time.sleep(SLEEP_TIME)
    # While the processing isn't complete
    while True:
        # Open the log file read only
        with open(matlab_log, "r") as fid:
            lines = fid.readlines()
        # Strip ending new line from all lines
        lines = [line.strip() for line in lines]
        # Check for the finished line
        if "########## Finished ##########" in lines:
            print("Matlab finished")
            break
        # Check for the failed line
        elif "########## Failed ##########" in lines:
            print("Matlab failed")
            # Throw error
            raise RuntimeError("Matlab processing failed")
        # Check to see if timeout has been exceeded
        if time.time() - t_start > START_TIMEOUT:
            # Kill the process
            proc.kill()
            # Print the error and raise a timeout error
            print('%.2fs Timelimit Exceeded', RUN_TIMEOUT)
            raise TimeoutError("Matlab execution timed out")
        print("Waiting for Matlab to finish.")
        time.sleep(SLEEP_TIME)