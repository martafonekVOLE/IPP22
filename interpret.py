# IPP 2022 Interpret
# Author: Martin Pech
import sys
from supportFiles import debug, runInterpret, exitCodes, switches

# Allow Debug Print (Stderr)
switches.allowDebugPrint = True
switches.allowDprint = True
debug.Print("Interpret.py started successfully")
debug.Print("=================================")

debug.Print("Switches status: ")
debug.Print("Allow debug print:" + str(switches.allowDebugPrint))
debug.Print("=================================")

# Interpret inicialization
inter = runInterpret.Interpret()

# Reading input files
XMLroot, checkStats, insts, hot, svars, statsOrder, openStats = inter.run(sys.argv)

# Checking input/source existence
if(inter.sourceInputHandler() >= 1):
    inputLines = inter.getInput()
    xml = runInterpret.XmlManager(XMLroot, inputLines, checkStats, insts, hot, svars, statsOrder, openStats)
    iterations = xml.children()
else:
    fix = []
    xml = runInterpret.XmlManager(XMLroot, fix, checkStats, insts, hot, svars, statsOrder, openStats)
    iterations = xml.children()

xml.checkLabels()

while True:
    xml.getNext()
    iterations -= 1

