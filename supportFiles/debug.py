import sys
from supportFiles import switches

def Print(message):
    if(switches.allowDebugPrint == True):
        sys.stderr.write(message + "\n")
        #print(message, sys.stderr) Another option

def Dprint(message):
    if(switches.allowDprint == True):
        sys.stderr.write(message + "\n")

    