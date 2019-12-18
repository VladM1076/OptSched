#!/usr/bin/python3
'''*******************************************************************************
Description:    This script is meant to be used with the OptSched scheduler and
                the run-plaidbench.sh script. This script will extract stats
                about how our OptSched scheduler is doing from the log files 
                generated from the run-plaidbench.sh script.
Author:	        Vang Thao
Last Update:	November 27, 2019
*******************************************************************************'''

'''
HOW TO USE:
    1.) Run a plaidbench benchmarks with run-plaidbench.sh to generate a
        directory containing the results for the run.
    2.) Copy this script to be in the same directory as the directory created.
        No other directory not generated by plaidbench.sh should be in the same
        location as this script.
    3.) Run this script to output the stats to the terminal.
'''

import os       # Used for scanning directories, getting paths, and checking files.
import re

REGEX_DAG_INFO = re.compile('Processing DAG (.*) with (\d+) insts and max latency (\d+)')
REGEX_LIST_OPTIMAL = re.compile('list schedule (.?)* is optimal')
REGEX_COST_IMPROV = re.compile('cost imp=(\d+).')
REGEX_OPTIMAL = re.compile('The schedule is optimal')
REGEX_PASS_NUM = re.compile(r"End of (.*) pass through")

# Contains all of the stats
benchStats = {}
passStats = {}

# List of benchmark names
benchmarks = [
    "densenet121",
    "densenet169",
    "densenet201",
    "inception_resnet_v2",
    "inception_v3",
    "mobilenet",
    "nasnet_large",
    "nasnet_mobile",
    "resnet50",
    "vgg16",
    "vgg19",
    "xception",
    "imdb_lstm",
]

# Get name of all directories in current folder
subfolders = [f.name for f in os.scandir(".") if f.is_dir() ]

# For each folder
for folderName in subfolders:
    # Get the run number from the end
    # of the folder name
    runNumber = folderName[-2:]

    # Get the name of the run
    # and exclude the run number
    nameOfRun = folderName[:-3]
        
    # Create an entry in the stats for the
    # name of the run
    if (nameOfRun not in benchStats):
        benchStats[nameOfRun] = {}

    # Begin stats collection for this run
    firstPassTotalProcessed = 0
    firstPassEnumCnt = 0
    firstPassOptImpr = 0
    firstPassOptNotImpr = 0
    firstPassTimeoutImpr = 0
    firstPassTimeoutNotImpr = 0
    firstPassTimeoutCnt = 0
    firstPassLargestOptimalRegion = -1
    firstPassLargestImprovedRegion = -1
    firstPassTotalInstr = 0
    
    secondPassTotalProcessed = 0
    secondPassEnumCnt = 0
    secondPassOptImpr = 0
    secondPassOptNotImpr = 0
    secondPassTimeoutImpr = 0
    secondPassTimeoutNotImpr = 0
    secondPassTimeoutCnt = 0
    secondPassLargestOptimalRegion = -1
    secondPassLargestImprovedRegion = -1
    secondPassTotalInstr = 0
   
    for bench in benchmarks:
        currentPath = os.path.join(folderName, bench)
        currentLogFile = os.path.join(currentPath, bench + ".log")

        # Contain the stats for this run
        benchPassesStats = {}
        benchPassesStats["First"] = {}
        benchPassesStats["Second"] = {}

        # Initialize stats variables
        benchPassesStats["First"]["regionsProcessed"] = 0
        benchPassesStats["First"]["enumCnt"] = 0
        benchPassesStats["First"]["OptImprov"] = 0
        benchPassesStats["First"]["OptNotImprov"] = 0
        benchPassesStats["First"]["TimeoutImprov"] = 0
        benchPassesStats["First"]["TimeoutNotImprov"] = 0
        benchPassesStats["First"]["timeoutCnt"] = 0
        benchPassesStats["First"]["largestOptimalRegion"] = -1
        benchPassesStats["First"]["largestImprovedRegion"] = -1
        benchPassesStats["First"]["totalInstr"] = 0
        
        benchPassesStats["Second"]["regionsProcessed"] = 0
        benchPassesStats["Second"]["enumCnt"] = 0
        benchPassesStats["Second"]["OptImprov"] = 0
        benchPassesStats["Second"]["OptNotImprov"] = 0
        benchPassesStats["Second"]["TimeoutImprov"] = 0
        benchPassesStats["Second"]["TimeoutNotImprov"] = 0
        benchPassesStats["Second"]["timeoutCnt"] = 0
        benchPassesStats["Second"]["largestOptimalRegion"] = -1
        benchPassesStats["Second"]["largestImprovedRegion"] = -1
        benchPassesStats["Second"]["totalInstr"] = 0
        
        # First check if log file exists.
        if (os.path.exists(currentLogFile)):
            benchStats[bench] = {}
            # Open log file if it exists.
            with open(currentLogFile) as file:
                inputFile = file.read()
                blocks = log.split("********** Opt Scheduling **********")[1:]
                for block in blocks:
                    # Get pass num
                    getPass = REGEX_PASS_NUM.search(block)
                    passNum = getPass.group(1)

                    benchPassesStats[passNum]["regionsProcessed"] += 1

                    # If our enumerator was called then
                    # record stats for it.
                    if ("Enumerating" in block):
                        benchPassesStats[passNum]["enumCnt"] += 1
                        # Get cost
                        searchCost = REGEX_COST_IMPROV.search(block)
                        cost = int(searchCost.group(1))

                        # Get DAG stats
                        dagInfo = REGEX_DAG_INFO.search(block)
                        numOfInstr = int(dagInfo.group(2))
                        benchPassesStats[passNum]["totalInstr"] += numOfInstr

                        if (REGEX_OPTIMAL.search(block)):
                            # Optimal and improved
                            if (cost > 0):
                                benchPassesStats[passNum]["OptImprov"] += 1
                                if (numOfInstr > benchPassesStats[passNum]["largestImprovedRegion"]):
                                    benchPassesStats[passNum]["largestImprovedRegion"] = numOfInstr
                            # Optimal but not improved
                            elif (cost == 0):
                                benchPassesStats[passNum]["OptNotImprov"] += 1
                            if (numOfInstr > benchPassesStats[passNum]["largestOptimalRegion"]):
                                benchPassesStats[passNum]["largestOptimalRegion"] = numOfInstr
                        elif ("timedout" in block):
                            # Timeout and improved
                            if (cost > 0):
                                benchPassesStats[passNum]["TimeoutImprov"] += 1
                                if (numOfInstr > benchPassesStats[passNum]["largestImprovedRegion"]):
                                    benchPassesStats[passNum]["largestImprovedRegion"] = numOfInstr
                            # Timeout but not improved
                            elif (cost == 0):
                                benchPassesStats[passNum]["TimeoutNotImprov"] += 1
                            benchPassesStats[passNum]["timeoutCnt"] += 1
                            
                                                        
        # If the file doesn't exist, output error log.
        else:
            print("Cannot find log file for {} run {} benchmark {}.".format(nameOfRun, runNumber, bench))

        firstPassTotalProcessed += benchPassesStats["First"]["regionsProcessed"]
        firstPassEnumCnt += benchPassesStats["First"]["enumCnt"]
        firstPassOptImpr += benchPassesStats["First"]["OptImprov"]
        firstPassOptNotImpr += benchPassesStats["First"]["OptNotImprov"]
        firstPassTimeoutImpr += benchPassesStats["First"]["TimeoutImprov"]
        firstPassTimeoutNotImpr += benchPassesStats["First"]["TimeoutNotImprov"]
        firstPassTimeoutCnt += benchPassesStats["First"]["timeoutCnt"]
        if (firstPassLargestOptimalRegion < benchPassesStats["First"]["largestOptimalRegion"]):
            firstPassLargestOptimalRegion = benchPassesStats["First"]["largestOptimalRegion"]
        if (firstPassLargestImprovedRegion < benchPassesStats["First"]["largestImprovedRegion"]):
            firstPassLargestImprovedRegion = benchPassesStats["First"]["largestImprovedRegion"]
        firstPassTotalInstr += benchPassesStats["First"]["totalInstr"]

        secondPassTotalProcessed += benchPassesStats["Second"]["regionsProcessed"]
        secondPassEnumCnt += benchPassesStats["Second"]["enumCnt"]
        secondPassOptImpr += benchPassesStats["Second"]["OptImprov"]
        secondPassOptNotImpr += benchPassesStats["Second"]["OptNotImprov"]
        secondPassTimeoutImpr += benchPassesStats["Second"]["TimeoutImprov"]
        secondPassTimeoutNotImpr += benchPassesStats["Second"]["TimeoutNotImprov"]
        secondPassTimeoutCnt += benchPassesStats["Second"]["timeoutCnt"]
        if (secondPassLargestOptimalRegion < benchPassesStats["Second"]["largestOptimalRegion"]):
            secondPassLargestOptimalRegion = benchPassesStats["Second"]["largestOptimalRegion"]
        if (secondPassLargestImprovedRegion < benchPassesStats["Second"]["largestImprovedRegion"]):
            secondPassLargestImprovedRegion = benchPassesStats["Second"]["largestImprovedRegion"]
        secondPassTotalInstr += benchPassesStats["Second"]["totalInstr"]

    print("{}".format(folderName))
    print("    First pass total regions processed: {}".format(firstPassTotalProcessed))
    print("    Regions passed to B&B: {} ({:.1f}%)".format(firstPassEnumCnt, float(firstPassEnumCnt)/firstPassTotalProcessed*100.0))
    print("    Regions optimal and improved: {} ({:.1f}%)".format(firstPassOptImpr, float(firstPassOptImpr)/firstPassEnumCnt*100.0))
    print("    Regions optimal and not improved: {} ({:.1f}%)".format(firstPassOptNotImpr, float(firstPassOptNotImpr)/firstPassEnumCnt*100.0))
    print("    Regions timed out and improved: {} ({:.1f}%)".format(firstPassTimeoutImpr, float(firstPassTimeoutImpr)/firstPassEnumCnt*100.0))
    print("    Regions timed out and not improved: {} ({:.1f}%)".format(firstPassTimeoutNotImpr, float(firstPassTimeoutNotImpr)/firstPassEnumCnt*100.0))
    print("    Avg. region size passed to B&B: {:.1f}".format(firstPassTotalInstr/firstPassEnumCnt))
    print("    Largest optimal region: {}".format(firstPassLargestOptimalRegion))
    print("    Largest improved region: {}".format(firstPassLargestImprovedRegion))
    print("      Second pass total regions processed: {}".format(secondPassTotalProcessed))
    print("      Regions passed to B&B: {} ({:.1f}%)".format(secondPassEnumCnt, float(secondPassEnumCnt)/secondPassTotalProcessed*100.0))
    print("      Regions optimal and improved: {} ({:.1f}%)".format(secondPassOptImpr, float(secondPassOptImpr)/secondPassEnumCnt*100.0))
    print("      Regions optimal and not improved: {} ({:.1f}%)".format(secondPassOptNotImpr, float(secondPassOptNotImpr)/secondPassEnumCnt*100.0))
    print("      Regions timed out and improved: {} ({:.1f}%)".format(secondPassTimeoutImpr, float(secondPassTimeoutImpr)/secondPassEnumCnt*100.0))
    print("      Regions timed out and not improved: {} ({:.1f}%)".format(secondPassTimeoutNotImpr, float(secondPassTimeoutNotImpr)/secondPassEnumCnt*100.0))
    print("      Avg. region size passed to B&B: {:.1f}".format(secondPassTotalInstr/secondPassEnumCnt))
    print("      Largest optimal region: {}".format(secondPassLargestOptimalRegion))
    print("      Largest improved region: {}".format(secondPassLargestImprovedRegion))