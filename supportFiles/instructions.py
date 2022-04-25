from supportFiles import debug
from supportFiles.exitCodes import *
import re

class Depth():
    def __init__(self):
        self.frames = []
        self.globalFrame = {}

        self.localFlag = False
        self.tempFlag = False
        self.invokedLocals = False
        self.pushCount = 0
        
        self.maxVarsCounter = 0

        self.dataStack = []

        debug.Print("Depth: Inicialized")

    def NewTempFrame(self):
        self.tempFrame = {}
        self.tempFlag = True

        debug.Print("Depth: New Temporary Frame")

    def NewLocalFrame(self):
        if(self.invokedLocals == False):
            self.localFrame = {}
            self.invokedLocals = True
        
        self.localFlag = True
        self.frames.append(self.localFrame)
        self.localFrame = self.tempFrame
        self.pushCount += 1

        self.tempFrame = {}
        self.tempFlag = False

        debug.Print("Depth: New Local Frame on stack")

    def PopOldFrame(self):
        if(self.pushCount == 0):
            debug.Print("Depth: Popping unexisting frame")
            exit(INVALID_FRAME)

        self.pushCount -= 1
        if(self.pushCount == 0):
            self.localFlag = False 
        
        self.tempFrame = self.localFrame
        self.localFrame = self.frames.pop()

        self.tempFlag = True

        debug.Print("Depth: Old Local Frame from stack")

    def returnValidString(self, occurrences, outputValue):
        limiter = 0
        for o in occurrences:
            try:
                o = int(o)
                o = o - limiter * 3
                transform = outputValue[o+1] + outputValue [o + 2] + outputValue [o + 3] 
                transform = chr(int(transform))
                outOne = outputValue[:(o)]
                outTwo = outputValue[(o+4):]
                outputValue = outOne + transform + outTwo
                limiter += 1
            except:
                # debug.Print("Invalid escape sequence")
                # exit(INVALID_STRING) 
                debug.Print("Backslash but no escape sequence")
            
        return(outputValue)
        


    # Instructions - each instruction (or most of them) 
    # does have own function, which is responsible for 
    # how the program behaves

    # Typically set of instructions has same manner
    # Usually you check input var existence or input type validity 
    # Then you do the operation which is pretty straight forward
    def MOVE(self, inputVarName, argType, inputArgValue):
        debug.Print('Instructions: MOVE')
        if(argType == "var"):
            argFrame, argValue = inputArgValue.split("@")
            if(argFrame == "GF"):
                if(argValue in self.globalFrame):
                    moveValue = self.globalFrame.get(argValue)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            elif(argFrame == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)

                if(argValue in self.localFrame):
                    moveValue = self.localFrame.get(argValue)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            elif(argFrame == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)

                if(argValue in self.tempFrame):
                    moveValue = self.tempFrame.get(argValue)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg, Invalid frame")
                exit(INVALID_VAR)
        elif(argType == "int" or argType == "bool" or argType == "string" or argType == "nil"):
            if(inputArgValue == None):
                moveValue = argType + "@"
            else:
                if(argType == "string"):    #
                    occurrences = self.findOccurrences(inputArgValue, '\\')
                    inputArgValue = self.returnValidString(occurrences, inputArgValue)
                
                moveValue = argType + "@" + inputArgValue   
        else:
            debug.Print("Invalid Argument, no var or type")
            exit(INVALID_VAR)      

        if(moveValue == None):
            debug.Print("Variable is type none")
            exit(MISSING_VALUE)
        
        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName in self.globalFrame):
                self.globalFrame[varName] = moveValue
            else:
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName in self.localFrame):
                self.localFrame[varName] = moveValue
            else:
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName in self.tempFrame):
                self.tempFrame[varName] = moveValue
            else:
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)

    # Set of instructions that works with data stack
    def CREATEFRAME(self):
        debug.Print('Instructions: CREATEFRAME')
        self.NewTempFrame()

    def PUSHFRAME(self):
        debug.Print('Instructions: PUSHFRAME')
        if(self.tempFlag == False):
            debug.Print("Frame does not exist")
            exit(INVALID_FRAME)

        self.NewLocalFrame()

    def POPFRAME(self):
        debug.Print('Instructions: POPFRAME')
        self.PopOldFrame()

    def DEFVAR(self, varValue):
        debug.Print('Instructions: DEFVAR')

        frameType, varName = varValue.split("@")
        if(frameType == "GF"):                               
            if(varName in self.globalFrame):
                debug.Print("This variable already exists in current frame!")
                exit(SEMANTICK_ERROR)
            else:
                self.globalFrame[varName] = None 

        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName in self.localFrame):
                debug.Print("This variable already exists in current frame!")
                exit(SEMANTICK_ERROR)
            else:
                self.localFrame[varName] = None

        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName in self.tempFrame):
                debug.Print("This variable already exists in current frame!")
                exit(SEMANTICK_ERROR)
            else:
                self.tempFrame[varName] = None
        else:
            debug.Print("Variable has no frame type")
            exit(INVALID_VAR)

    def CALL(self):
        debug.Print('Instructions: CALL')

    def RETURN(self):
        debug.Print('Instructions: RETURN')

    def PUSHS(self, value, inputType):
        debug.Print('Instructions: PUSHS')
        if(inputType == "var"):
            frameType, varName = value.split("@")
            if(frameType == "GF"):
                if(varName in self.globalFrame):
                    if not (self.globalFrame.get(varName) == None):
                        self.dataStack.append(self.globalFrame.get(varName))
                    else: 
                        debug.Print("Variable has no value")
                        exit(MISSING_VALUE)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            elif(frameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName in self.localFrame):
                    if not (self.localFrame.get(varName) == None):
                        self.dataStack.append(self.localFrame.get(varName))
                    else: 
                        debug.Print("Variable has no value")
                        exit(MISSING_VALUE)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            elif(frameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName in self.tempFrame):
                    if not (self.tempFrame.get(varName) == None):
                        self.dataStack.append(self.tempFrame.get(varName))
                    else: 
                        debug.Print("Variable has no value")
                        exit(MISSING_VALUE)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Invalid frame type")
                exit(INVALID_VAR)

        elif(inputType == "int" or inputType == "string" or inputType == "bool" or inputType == "nil"): 
            if(inputType == "nil"):
                self.dataStack.append("nil@nil")
            else:    
                self.dataStack.append(inputType + "@" + value)
        else:
            debug.Print("Invalid push")
            exit(INVALID_VAR)

    def POPS(self, inputVarName):
        debug.Print('Instructions: POPS')
        if not (len(self.dataStack) == 0):
            frameType, varName = inputVarName.split("@")
            if(frameType == "GF"):
                if(varName in self.globalFrame):
                    self.globalFrame[varName] = self.dataStack.pop()
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            elif(frameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName in self.localFrame):
                    self.localFrame[varName] = self.dataStack.pop()
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            elif(frameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName in self.tempFrame):
                    self.tempFrame[varName] = self.dataStack.pop()
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Invalid frame type")
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE) 

    # set of instructions that check var existence, and two types validity
    def ADD(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):
        debug.Print('Instructions: ADD')

        if not (firstOpType == "int" or firstOpType == "var" and secondOpType == "int" or secondOpType == "var"):
            debug.Print("Canot use arithmetical operations on other types")
            exit(WRONG_OPERANDS)

        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
        if(firstOpType == "var"):
            firstVal = 0
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:                                       
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else: 
                debug.Print("Arg1, invalid data frame")
                exit(INVALID_FRAME)
            try:
                checkInt, firstVal = firstVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)
            
            if not (checkInt == "int"):
                debug.Print("Arg1, Variable is not INT")
                exit(INVALID_VAR)

        if(secondOpType == "var"):
            secondVal = 0
            secondFrameType, secondVarName = secondOpValue.split("@")
            if(secondFrameType == "GF"):
                if(secondVarName in self.globalFrame):
                    secondVal = self.globalFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.localFrame):
                    secondVal = self.localFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.tempFrame):
                    secondVal = self.tempFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg2, invalid frame")
                exit(INVALID_FRAME)
            try: 
                checkInt, secondVal = secondVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)

            if not (checkInt == "int"):
                debug.Print("Arg2, Variable is not INT")
                exit(INVALID_VAR)

        if(firstOpType == "int"):
            firstVal = firstOpValue

        if(secondOpType == "int"):
            secondVal = secondOpValue


        try: 
            if(frameType == "GF"):
                self.globalFrame[varName] = "int@" + str(int(float(firstVal)) + int(float(secondVal)))        
            elif(frameType == "LF"):
                self.localFrame[varName] = "int@" + str(int(float(firstVal)) + int(float(secondVal)))
            elif(frameType == "TF"):
                self.tempFrame[varName] = "int@" + str(int(float(firstVal)) + int(float(secondVal)))    
            else:
                debug.Print("Invalid frame type")
                exit(INVALID_VAR)
        except:
            debug.Print("Incorrect instruction type")
            exit(WRONG_OPERANDS)



    def SUB(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):
        debug.Print('Instructions: SUB')

        if not(firstOpType == "int" or firstOpType == "var" and secondOpType == "int" or secondOpType == "var"):
            debug.Print("Canot use arithmetical operations on other types")
            exit(WRONG_OPERANDS)

        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag== False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_FRAME)

        if(firstOpType == "var"):
            firstVal = 0
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg1, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                checkInt, firstVal = firstVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)
            
            if not(checkInt == "int"):
                debug.Print("Arg1, Variable is not INT")
                exit(INVALID_VAR)

        if(secondOpType == "var"):
            secondVal = 0
            secondFrameType, secondVarName = secondOpValue.split("@")
            if(secondFrameType == "GF"):
                if(secondVarName in self.globalFrame):
                    secondVal = self.globalFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.localFrame):
                    secondVal = self.localFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.tempFrame):
                    secondVal = self.tempFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg2, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                checkInt, secondVal = secondVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)

            if not (checkInt == "int"):
                debug.Print("Arg2, Variable is not INT")
                exit(INVALID_VAR)

        if(firstOpType == "int"):
            firstVal = firstOpValue

        if(secondOpType == "int"):
            secondVal = secondOpValue

        try:   
            if(frameType == "GF"):
                self.globalFrame[varName] = "int@" + str(int(float(firstVal)) - int(float(secondVal)))
            elif(frameType == "LF"):
                self.localFrame[varName] = "int@" + str(int(float(firstVal)) - int(float(secondVal)))
            elif(frameType == "TF"):
                self.tempFrame[varName] = "int@" + str(int(float(firstVal)) - int(float(secondVal)))    
            else:
                debug.Print("Invalid frame type")
                exit(INVALID_VAR)
        except:
            debug.Print("Incorrect instruction type")
            exit(WRONG_OPERANDS)

    def MUL(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):

        if not (firstOpType == "int" or firstOpType == "var" and secondOpType == "int" or secondOpType == "var"):
            debug.Print("Canot use arithmetical operations on other types")
            exit(WRONG_OPERANDS)

        debug.Print('Instructions: MUL')
        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
        if(firstOpType == "var"):
            firstVal = 0
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg1, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                checkInt, firstVal = firstVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)
            
            if not (checkInt == "int"):
                debug.Print("Arg1, Variable is not INT")
                exit(INVALID_VAR)

        if(secondOpType == "var"):
            secondVal = 0
            secondFrameType, secondVarName = secondOpValue.split("@")
            if(secondFrameType == "GF"):
                if(secondVarName in self.globalFrame):
                    secondVal = self.globalFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.localFrame):
                    secondVal = self.localFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.tempFrame):
                    secondVal = self.tempFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg2, Invalid data frame")
                exit(INVALID_FRAME)
            
            try:
                checkInt, secondVal = secondVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)
            
            if not (checkInt == "int"):
                debug.Print("Arg2, Variable is not INT")
                exit(INVALID_VAR)

        if(firstOpType == "int"):
            firstVal = firstOpValue

        if(secondOpType == "int"):
            secondVal = secondOpValue

        try:
            if(frameType == "GF"):
                self.globalFrame[varName] = "int@" + str(int(float(firstVal)) * int(float(secondVal)))
            elif(frameType == "LF"):
                self.localFrame[varName] = "int@" + str(int(float(firstVal)) * int(float(secondVal)))
            elif(frameType == "TF"):
                self.tempFrame[varName] = "int@" + str(int(float(firstVal)) * int(float(secondVal)))    
            else:
                debug.Print("Invalid frame type")
                exit(INVALID_VAR)
        except:
            debug.Print("Incorrect instruction type")
            exit(WRONG_OPERANDS)

    def IDIV(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):

        if not ((firstOpType == "int" or firstOpType == "var") and (secondOpType == "int" or secondOpType == "var")): 
            debug.Print("Canot use arithmetical operations on other types")
            exit(WRONG_OPERANDS)
            
        debug.Print('Instructions: IDIV')
        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
        if(firstOpType == "var"):
            firstVal = 0
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg1, Invalid data frame")
                exit(INVALID_FRAME)

            try: 
                checkInt, firstVal = firstVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)

            if not (checkInt == "int"):
                debug.Print("Arg1, Variable is not INT")
                exit(INVALID_VAR)

        if(secondOpType == "var"):
            secondVal = 0
            secondFrameType, secondVarName = secondOpValue.split("@")
            if(secondFrameType == "GF"):
                if(secondVarName in self.globalFrame):
                    secondVal = self.globalFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.localFrame):
                    secondVal = self.localFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.tempFrame):
                    secondVal = self.tempFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg2, Invalid data frame")
                exit(INVALID_FRAME)
            
            try:
                checkInt, secondVal = secondVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)

            if not (checkInt == "int"):
                debug.Print("Arg2, Variable is not INT")
                exit(INVALID_VAR)

        if(firstOpType == "int"):
            firstVal = firstOpValue

        if(secondOpType == "int"):
            secondVal = secondOpValue

        if(int(secondVal) == 0):
            debug.Print("Division by zero")
            exit(INVALID_OPERAND_VALUE)

        try:
            if(frameType == "GF"):
                self.globalFrame[varName] = "int@" + str(int(float(firstVal) / float(secondVal)))  
            elif(frameType == "LF"):
                self.localFrame[varName] = "int@" + str(int(float(firstVal) / float(secondVal)))
            elif(frameType == "TF"):
                self.tempFrame[varName] = "int@" + str(int(float(firstVal) / float(secondVal)))   
            else:
                debug.Print("Invalid frame type")
                exit(INVALID_VAR)
        except:
            debug.Print("Incorrect instruction type")
            exit(WRONG_OPERANDS)

    def LT(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):
        debug.Print('Instructions: LT')
        if(firstOpType == "var"):
            varType, varName = firstOpValue.split("@")      
            if(varType == "GF"):
                if(varName not in self.globalFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstCompare = self.globalFrame.get(varName)
            elif(varType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.localFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstCompare = self.localFrame.get(varName)
            elif(varType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.tempFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstCompare = self.tempFrame.get(varName)
        else:
            if(firstOpType == "int" or firstOpType == "string" or firstOpType == "bool"):
                if(firstOpValue == None and firstOpType == "string"):
                    firstOpValue = ""
                firstCompare = firstOpType + "@" + firstOpValue
            else:
                debug.Print("Arg1, invalid type")
                exit(WRONG_OPERANDS)
                

        # second OP
        if(secondOpType == "var"):
            varType, varName = secondOpValue.split("@")      
            if(varType == "GF"):
                if(varName not in self.globalFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    secondCompare = self.globalFrame.get(varName)
            elif(varType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.localFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    secondCompare = self.localFrame.get(varName)
            elif(varType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.tempFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    secondCompare = self.tempFrame.get(varName)
        else:
            if(secondOpType == "int" or secondOpType == "string" or secondOpType == "bool"):
                if(secondOpValue == None and secondOpType == "string"):
                    secondOpValue = ""
                secondCompare = secondOpType + "@" + secondOpValue
            else:
                debug.Print("Arg2, invalid type")
                exit(WRONG_OPERANDS)
        
        # Comparison
        firstType = 0
        secondType = 0

        try:
            firstType, firstName = firstCompare.split("@")
            secondType, secondName = secondCompare.split("@")
        except:
            debug.Print("Variable is no type")
            exit(MISSING_VALUE)

        result = "false"

        if not (firstType == secondType):
            debug.Print("Instructions types do not match")
            exit(WRONG_OPERANDS)
        
        else:
            if(firstType == "int"):
                firstName = int(float(firstName))
                secondName = int(float(secondName))
                if(firstName < secondName):
                    result = "true"
            elif(firstType == "bool"):
                if(firstName == "false" and secondName == "true"):
                    result = "true"
            else:
                if(firstType == "string"):
                    occurrences = self.findOccurrences(firstName, '\\')
                    firstName = self.returnValidString(occurrences, firstName)
                if(secondType == "string"):
                    occurrences = self.findOccurrences(secondName, '\\')
                    secondName = self.returnValidString(occurrences, secondName)

                if(firstName < secondName):
                    result = "true"

        
        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                self.globalFrame[varName] = "bool@" + result
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                self.globalFrame[varName] = "bool@" + result
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                self.globalFrame[varName] = "bool@" + result
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
    def GT(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):
        debug.Print('Instructions: GT')
        if(firstOpType == "var"):
            varType, varName = firstOpValue.split("@")      
            if(varType == "GF"):
                if(varName not in self.globalFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstCompare = self.globalFrame.get(varName)
            elif(varType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.localFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstCompare = self.localFrame.get(varName)
            elif(varType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.tempFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstCompare = self.tempFrame.get(varName)
        else:
            if(firstOpType == "int" or firstOpType == "string" or firstOpType == "bool"):
                if(firstOpType == "string" and firstOpValue == None):
                    secondOpValue = ""
                firstCompare = firstOpType + "@" + firstOpValue
            else:
                debug.Print("Arg1, invalid type")
                exit(WRONG_OPERANDS)
                

        # second OP
        if(secondOpType == "var"):
            varType, varName = secondOpValue.split("@")      
            if(varType == "GF"):
                if(varName not in self.globalFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    secondCompare = self.globalFrame.get(varName)
            elif(varType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.localFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    secondCompare = self.localFrame.get(varName)
            elif(varType == "TF"):
                if(self.tempFlag== False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.tempFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    secondCompare = self.tempFrame.get(varName)
        else:
            if(secondOpType == "int" or secondOpType == "string" or secondOpType == "bool"):
                if(secondOpType == "string" and secondOpValue == None):
                    secondOpValue = ""
                secondCompare = secondOpType + "@" + secondOpValue
            else:
                debug.Print("Arg2, invalid type")
                exit(WRONG_OPERANDS)
        
        # Comparison
        firstType = 0
        secondType = 0
        try:
            firstType, firstName = firstCompare.split("@")
            secondType, secondName = secondCompare.split("@")
        except:
            debug.Print("Variable is no type")
            exit(MISSING_VALUE)

        result = "false"

        if not (firstType == secondType):
            debug.Print("Instructions types do not match")
            exit(WRONG_OPERANDS)
        
        else:
            if(firstType == "int"):
                firstName = int(float(firstName))
                secondName = int(float(secondName))
                if(firstName > secondName):
                    result = "true"
            elif(firstType == "bool"):
                if(firstName == "true" and secondName == "false"):
                    result = "true"
            else:
                if(firstType == "string"):
                    occurrences = self.findOccurrences(firstName, '\\')
                    firstName = self.returnValidString(occurrences, firstName)
                if(secondType == "string"):
                    occurrences = self.findOccurrences(secondName, '\\')
                    secondName = self.returnValidString(occurrences, secondName)

                if(firstName > secondName):
                    result = "true"

        
        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                self.globalFrame[varName] = "bool@" + result
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                self.globalFrame[varName] = "bool@" + result
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                self.globalFrame[varName] = "bool@" + result
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
    def EQ(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):
        debug.Print('Instructions: EQ')
        if(firstOpType == "var"):
            varType, varName = firstOpValue.split("@")      
            if(varType == "GF"):
                if(varName not in self.globalFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstCompare = self.globalFrame.get(varName)
            elif(varType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.localFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstCompare = self.localFrame.get(varName)
            elif(varType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.tempFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstCompare = self.tempFrame.get(varName)
        else:
            if(firstOpType == "int" or firstOpType == "string" or firstOpType == "bool" or firstOpType == "nil"):
                firstCompare = firstOpType + "@" + firstOpValue
            else:
                debug.Print("Arg1, invalid type")
                exit(WRONG_OPERANDS)
                

        # second OP
        if(secondOpType == "var"):
            varType, varName = secondOpValue.split("@")      
            if(varType == "GF"):
                if(varName not in self.globalFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    secondCompare = self.globalFrame.get(varName)
            elif(varType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.localFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    secondCompare = self.localFrame.get(varName)
            elif(varType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.tempFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    secondCompare = self.tempFrame.get(varName)
        else:
            if(secondOpType == "int" or secondOpType == "string" or secondOpType == "bool" or secondOpType == "nil"):
                if(secondOpValue == None):
                    secondCompare = secondOpType + "@"
                else:
                    secondCompare = secondOpType + "@" + secondOpValue
            else:
                debug.Print("Arg2, invalid type")
                exit(WRONG_OPERANDS)
        
        # Comparison
        firstType = 0
        secondType = 0

        try:
            firstType, firstName = firstCompare.split("@")
            secondType, secondName = secondCompare.split("@")
        except:
            debug.Print("Variable is no type")
            exit(MISSING_VALUE)

        result = "false"

        if(firstType == "nil" or secondType == "nil"):
            if(firstType == "nil" and secondType == "nil"):
                result = "true"
            else:
                result = "false"

        elif not (firstType == secondType):                      
            debug.Print("Instructions types do not match")
            exit(WRONG_OPERANDS)
        
        else:
            if(firstType == "int"):
                firstName = int(float(firstName))
                secondName = int(float(secondName))
                if(firstName == secondName):
                    result = "true"
            elif(firstType == "bool"):
                if((firstName == "true" and secondName == "true") or (firstName == "false" and secondName == "false")):
                    result = "true"
            else:
                if(firstType == "string"):
                    occurrences = self.findOccurrences(firstName, '\\')
                    firstName = self.returnValidString(occurrences, firstName)
                if(secondType == "string"):
                    occurrences = self.findOccurrences(secondName, '\\')
                    secondName = self.returnValidString(occurrences, secondName)
                
                if(firstName == secondName):
                    result = "true"

        
        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                self.globalFrame[varName] = "bool@" + result
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                self.globalFrame[varName] = "bool@" + result
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                self.globalFrame[varName] = "bool@" + result
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)

    # logical and
    def logAND(self, firstOpValue, secondOpValue):
        debug.Print("Instructions: logAND")
        if((firstOpValue == "true" or firstOpValue == "false") and (secondOpValue == "true" or secondOpValue == "false")):
            if(firstOpValue == "true" and secondOpValue == "true"):
                return "true"
            else:
                return "false"
        else:
            debug.Print("Expected bool, given something else")
            exit(WRONG_OPERANDS)

    def AND(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):
        debug.Print('Instructions: AND')

        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
        if(firstOpType == "var"):
            firstVal = 0
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg1, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                checkInt, firstVal = firstVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)

            if not (checkInt == "bool"):
                debug.Print("Arg1, Variable is not INT")
                exit(INVALID_VAR)

        if(secondOpType == "var"):
            secondVal = 0
            secondFrameType, secondVarName = secondOpValue.split("@")
            if(secondFrameType == "GF"):
                if(secondVarName in self.globalFrame):
                    secondVal = self.globalFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.localFrame):
                    secondVal = self.localFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME) 
                if(secondVarName in self.tempFrame):
                    secondVal = self.tempFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg2, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                checkInt, secondVal = secondVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)

            if not (checkInt == "bool"):
                debug.Print("Arg2, Variable is not INT")
                exit(INVALID_VAR)

        if(firstOpType == "bool"):
            firstVal = firstOpValue

        if(secondOpType == "bool"):
            secondVal = secondOpValue

        try:
            if(frameType == "GF"):
                self.globalFrame[varName] = "bool@" + self.logAND(firstVal, secondVal)    
            elif(frameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                self.localFrame[varName] = "bool@" + self.logAND(firstVal, secondVal)
            elif(frameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                self.tempFrame[varName] = "bool@" + self.logAND(firstVal, secondVal)
            else:
                debug.Print("Invalid frame type")
                exit(INVALID_VAR)
        except:
            debug.Print("Incorrect instruction type")
            exit(WRONG_OPERANDS)

    # logical or
    def logOR(self, firstOpValue, secondOpValue):
        debug.Print("Instruction: logOR")
        if((firstOpValue == "true" or firstOpValue == "false") and (secondOpValue == "true" or secondOpValue == "false")):
            if(firstOpValue == "false" and secondOpValue == "false"):
                return "false"
            else:
                return "true"
        else:
            debug.Print("Expected bool, given something else")
            exit(WRONG_OPERANDS)

    def OR(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):
        debug.Print('Instructions: OR')

        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
        if(firstOpType == "var"):
            firstVal = 0
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)      
            else:
                debug.Print("Arg1, Invalid data frame")
                exit(INVALID_VAR)
            try:
                checkInt, firstVal = firstVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)
            
            if not (checkInt == "bool"):
                debug.Print("Arg1, Variable is not INT")
                exit(INVALID_VAR)

        if(secondOpType == "var"):
            secondVal = 0
            secondFrameType, secondVarName = secondOpValue.split("@")
            if(secondFrameType == "GF"):
                if(secondVarName in self.globalFrame):
                    secondVal = self.globalFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.localFrame):
                    secondVal = self.localFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.tempFrame):
                    secondVal = self.tempFrame.get(secondVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg2, Invalid data frame")
                exit(INVALID_VAR)
            try:
                checkInt, secondVal = secondVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)
            
            if not (checkInt == "bool"):
                debug.Print("Arg2, Variable is not INT")
                exit(INVALID_VAR)

        if(firstOpType == "bool"):
            firstVal = firstOpValue

        if(secondOpType == "bool"):
            secondVal = secondOpValue
        try:
            if(frameType == "GF"):
                self.globalFrame[varName] = "bool@" + self.logOR(firstVal, secondVal)    
            elif(frameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                self.localFrame[varName] = "bool@" + self.logOR(firstVal, secondVal)
            elif(frameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                self.tempFrame[varName] = "bool@" + self.logOR(firstVal, secondVal)
            else:
                debug.Print("Invalid frame type")
                exit(INVALID_VAR)
        except:
            debug.Print("Incorrect instruction type")
            exit(WRONG_OPERANDS)

    # set of instructions that only check var validity and one type
    def NOT(self, inputVarName, firstOpType, firstOpValue):
        debug.Print('Instructions: NOT')
        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)

        if(firstOpType == "var"):
            firstVal = 0
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg1, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                checkInt, firstVal = firstVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)
                
            if not (checkInt == "bool"):
                debug.Print("Arg1, Variable is not BOOL")
                exit(WRONG_OPERANDS)

        if(firstOpType == "bool"):
            firstVal = firstOpValue

        # solution
        try:
            if(firstVal == "true"):
                firstVal = "false"
            elif(firstVal == "false"):
                firstVal = "true"
            else:
                debug.Print("Invalid bool value")
                exit(WRONG_OPERANDS)
        except:
            debug.Print("Wrong Operands")
            exit(WRONG_OPERANDS)

        if(frameType == "GF"):
            self.globalFrame[varName] = "bool@" + firstVal    

        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            self.localFrame[varName] = "bool@" + firstVal
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            self.tempFrame[varName] = "bool@" + firstVal
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
                
    def INT2CHAR(self, inputVarName, firstOpType, firstOpValue):
        debug.Print('Instructions: INT2CHAR')

        if(firstOpType == "int"):
            firstOpValue = int(firstOpValue)
        
        elif(firstOpType == "var"):
            firstVarType, firstVarName = firstOpValue.split("@")

            if(firstVarType == "GF"):
                if(firstVarName not in self.globalFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstOpValue = self.globalFrame.get(firstVarName)
                    try:
                        firstOpType, firstOpValue = firstOpValue.split("@")
                    except:
                        debug.Print("Variable is no type")
                        exit(MISSING_VALUE)
                    if not (firstOpType == "int"):
                        debug.Print("Expected int, given something else")
                        exit(WRONG_OPERANDS)

            elif(firstVarType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName not in self.localFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstOpValue = self.localFrame.get(firstVarName)
                    try:
                        firstOpType, firstOpValue = firstOpValue.split("@")
                    except:
                        debug.Print("Variable is no type")
                        exit(MISSING_VALUE)
                    if not (firstOpType == "int"):
                        debug.Print("Expected int, given something else")
                        exit(WRONG_OPERANDS)
            
            elif(firstVarType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName not in self.tempFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    firstOpValue = self.tempFrame.get(firstVarName)
                    try:
                        firstOpType, firstOpValue = firstOpValue.split("@")
                    except:
                        debug.Print("Variable is no type")
                        exit(MISSING_VALUE)
                    if not (firstOpType == "int"):
                        debug.Print("Expected int, given something else")
                        exit(WRONG_OPERANDS)
            else:
                debug.Print("Invalid frame type1")
                exit(INVALID_VAR)

        else:
            debug.Print("Invalid type")
            exit(WRONG_OPERANDS)
        
        inputVarType, inputVarName = inputVarName.split("@")
        if(inputVarType == "GF"):
            if(inputVarName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            try:
                self.globalFrame[inputVarName] = "string@" + (chr(int(firstOpValue)))
            except:
                debug.Print("Expected number, something else given")
                exit(INVALID_STRING)


        elif(inputVarType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(inputVarName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
                
            try:
                self.localFrame[inputVarName] = "string@" + (chr(int(firstOpValue)))
            except:
                debug.Print("Expected number, something else given")
                exit(INVALID_STRING)

        elif(inputVarType == "TF"):
            if(self.tempFlag== False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(inputVarName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
                
            try:
                self.tempFrame[inputVarName] = "string@" + (chr(int(firstOpValue)))
            except:
                debug.Print("Expected number, something else given")
                exit(INVALID_STRING)
        else:
            debug.Print("Invalid frame type")
            exit(WRONG_OPERANDS)

    def STRI2INT(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue): 
        debug.Print('Instructions: STRI2INT')

        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
        if(firstOpType == "var"):
            firstVal = 0
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg1, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                firstType, firstVal = firstVal.split("@")
            except:
                debug.Print("Missing value")
                exit(MISSING_VALUE)

        if(secondOpType == "var"):
            secondVal = 0
            secondFrameType, secondVarName = secondOpValue.split("@")
            if(secondFrameType == "GF"):
                if(secondVarName in self.globalFrame):
                    secondVal = self.globalFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.localFrame):
                    secondVal = self.localFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.tempFrame):
                    secondVal = self.tempFrame.get(secondVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg2, Invalid data frame")
                exit(INVALID_FRAME)
            
            try:
                secondType, secondVal = secondVal.split("@")
            except:
                debug.Print("Missing value")
                exit(MISSING_VALUE)

            if not (secondType == "int"):
                debug.Print("Expected int value")
                exit(WRONG_OPERANDS)

        if(firstOpType == "string"):
            firstVal = firstOpValue
        else:
            debug.Print("Expected string value")
            exit(WRONG_OPERANDS)

        if(secondOpType == "int"):
            secondVal = secondOpValue
        else:
            debug.Print("Expected int value")
            exit(WRONG_OPERANDS)


        length = len(firstVal)
        if(int(secondVal) > (length-1) or int(secondVal) < 0):
            debug.Print("Outside the range") 
            exit(INVALID_STRING)
        else:
            result = firstVal[int(secondVal)]       

        if(frameType == "GF"):
            self.globalFrame[varName] = "int@" + str(ord(result))  
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            self.localFrame[varName] = "int@" + str(ord(result))
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            self.tempFrame[varName] = "int@" + str(ord(result))
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)

    # Read -> reads from file or stdin
    def READ(self, inputVarName, inType, line):
        debug.Print('Instructions: READ')

        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)

        if not (line == ""):
            value = line
        else:
            try:
                value = input()
            except:
                value = "nil@nil"


        value = value.strip() #strips whitespaces

        frameType, varName = inputVarName.split("@")        

        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                if(inType == "bool"):
                    if(re.match('^true$', str(value), re.IGNORECASE)):
                        self.globalFrame[varName] = "bool@true"

                    elif(re.match('^false$', str(value), re.IGNORECASE)):
                        self.globalFrame[varName] = "bool@false"

                    elif( not ((re.match('^false$', str(value), re.IGNORECASE)) or (re.match('^true$', str(value) ,re.IGNORECASE))) and (not str(value) == "")):
                        self.globalFrame[varName] = "bool@false"
                    
                    else:
                        self.globalFrame[varName] = "nil@nil"

                elif(inType == "int"):
                    try:
                        int(value)
                        self.globalFrame[varName] = "int@" + str(value)
                    except:
                        self.globalFrame[varName] = "nil@nil"

                else:
                    if(value == "nil@nil"):
                        self.globalFrame[varName] = "nil@nil"
                    else:
                        self.globalFrame[varName] = inType + "@" + str(value)


        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                if(inType == "bool"):
                    if(re.match('^true$', str(value) ,re.IGNORECASE)):
                        self.localFrame[varName] = "bool@true"

                    elif(re.match('^false$', str(value), re.IGNORECASE)):
                        self.localFrame[varName] = "bool@false"

                    elif( not ((re.match('^false$', str(value), re.IGNORECASE)) or (re.match('^true$', str(value) ,re.IGNORECASE))) and (not str(value) == "")):
                        self.localFrame[varName] = "bool@false"
                    
                    else:
                        self.localFrame[varName] = "nil@nil"

                elif(inType == "int"):
                    try:
                        int(value)
                        self.localFrame[varName] = "int@" + str(value)
                    except:
                        self.localFrame[varName] = "nil@nil"
                else:
                    if(value == "nil@nil"):
                        self.localFrame[varName] = "nil@nil"
                    else:
                        self.localFrame[varName] = inType + "@" + str(value)
        
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
            else:
                if(inType == "bool"):
                    if(re.match('^true$', str(value) ,re.IGNORECASE)):
                        self.tempFrame[varName] = "bool@true"

                    elif(re.match('^false$', str(value), re.IGNORECASE)):
                        self.tempFrame[varName] = "bool@false"

                    elif( not ((re.match('^false$', str(value), re.IGNORECASE)) or (re.match('^true$', str(value) ,re.IGNORECASE))) and (not str(value) == "")):
                        self.tempFrame[varName] = "bool@false"
                    
                    else:
                        self.tempFrame[varName] = "nil@nil"

                elif(inType == "int"):
                    try:
                        int(value)
                        self.tempFrame[varName] = "int@" + str(value)
                    except:
                        self.tempFrame[varName] = "nil@nil"
                else:
                    if(value == "nil@nil"):
                        self.globalFrame[varName] = "nil@nil"
                    else:
                        self.tempFrame[varName] = inType + "@" + str(value)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)

    def findOccurrences(self, inString, character):
        return [i for i, letter in enumerate(inString) if letter == character]

    def WRITE(self, inputType, inputValue):
        debug.Print('Instructions: WRITE')
        if(inputType == "var"):
            varType, varName = inputValue.split("@")
            if(varType == "GF"):
                if(self.globalFrame == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.globalFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    toPrint = self.globalFrame.get(varName)

                    if(toPrint == None):
                        debug.Print("Uninitialized variable")
                        exit(MISSING_VALUE)

            elif(varType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(varName not in self.localFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    toPrint = self.localFrame.get(varName)
                    if(toPrint == None):
                        debug.Print("Uninitialized variable")
                        exit(MISSING_VALUE)
            elif(varType == "TF"):
                if(self.tempFlag == False):   
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)

                if(varName not in self.tempFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    toPrint = self.tempFrame.get(varName)
                    if(toPrint == None):
                        debug.Print("Uninitialized variable")
                        exit(MISSING_VALUE)
            else:
                debug.Print("Invalid Frame type")
                exit(INVALID_FRAME)
        else:
            if(inputType == "int" or inputType == "string" or inputType == "bool" or inputType == "nil"):
                toPrint = inputType + "@" + inputValue
            else:
                debug.Print("Error, invalid data type")
                exit(WRONG_OPERANDS)

        outputType, outputValue = toPrint.split("@", 1) 
        
        if(outputType == "bool" or outputType == "nil"):
            if(outputType == "bool"):
                if((re.match('^true$', str(outputValue), re.IGNORECASE))):
                    print("true", end = '')
                elif((re.match('^false$', str(outputValue), re.IGNORECASE))):
                    print("false", end = '')

            elif(outputType == "nil" and outputValue == "nil"):
                print("", end = '')
            else:
                debug.Print("Invalid print type")
                exit(WRONG_OPERANDS)
        else:
            occurrences = self.findOccurrences(outputValue, '\\')
            if(len(occurrences) == 0):
                print((outputValue), end = '')        
            else:
                outputValue = self.returnValidString(occurrences, outputValue)
                print((outputValue), end = '')

    def CONCAT(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):
        debug.Print('Instructions: CONCAT')
        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
        if(firstOpType == "var"):
            firstVal = ""
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg1, Invalid data frame")
                exit(INVALID_FRAME)

            try:
                firstArgType, firstArgVal = firstVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)
            
        if(secondOpType == "var"):
            secondVal = ""
            secondFrameType, secondVarName = secondOpValue.split("@")
            if(secondFrameType == "GF"):
                if(secondVarName in self.globalFrame):
                    secondVal = self.globalFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.localFrame):
                    secondVal = self.localFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.tempFrame):
                    secondVal = self.tempFrame.get(secondVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg2, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                secondArgType, secondArgVal = secondVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)

        if(firstOpType == "int" or firstOpType == "string" or firstOpType == "bool"): 
            firstArgVal = firstOpValue
            firstArgType = firstOpType

        if(secondOpType == "int" or secondOpType == "string" or secondOpType == "bool"):
            secondArgVal = secondOpValue
            secondArgType = secondOpType

        try:
            if not (firstArgType == secondArgType):
                debug.Print("Operand types are not same")
                exit(WRONG_OPERANDS)
        except:
            debug.Print("Wrong operands")
            exit(WRONG_OPERANDS)

        if(firstArgVal == None):
            firstArgVal = ""
        
        if(secondArgVal == None):
            secondArgVal = ""

        if(frameType == "GF"):
            self.globalFrame[varName] = firstArgType + "@" + firstArgVal + secondArgVal    
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            self.localFrame[varName] = firstArgType +  "@" + firstArgVal + secondArgVal     
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            self.tempFrame[varName] = firstArgType +  "@" + firstArgVal + secondArgVal     
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)


    def STRLEN(self, inputVarName, argType, inputArgValue):
        debug.Print('Instructions: STRLEN')
            
        if(argType == "var"):
            argFrame, argValue = inputArgValue.split("@")
            if(argFrame == "GF"):
                if(argValue in self.globalFrame):
                    if not(self.globalFrame.get(argValue) == None):
                        moveValue = self.globalFrame.get(argValue)
                    else:
                        debug.Print("Variable does not have any type")
                        exit(MISSING_VALUE)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            elif(argFrame == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(argValue in self.localFrame):
                    if not(self.localFrame.get(argValue) == None):
                        moveValue = self.localFrame.get(argValue)
                    else:
                        debug.Print("Variable does not have any type")
                        exit(MISSING_VALUE)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            elif(argFrame == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(argValue in self.tempFrame):
                    if not (self.tempFrame.get(argValue) == None):
                        moveValue = self.tempFrame.get(argValue)
                    else:
                        debug.Print("Variable does not have any type")
                        exit(MISSING_VALUE)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg, Invalid frame")
                exit(INVALID_VAR)

            checkString, _ = moveValue.split("@")
            if not (checkString == "string"):
                exit(WRONG_OPERANDS)

        elif(argType == "string"): 
            if(inputArgValue == None):
                moveValue = argType + "@"                  
            else:
                moveValue = argType + "@" + inputArgValue 
        else:
            debug.Print("Invalid Argument, no var or type")
            exit(WRONG_OPERANDS)      
        
        moveType, moveString = moveValue.split("@")
        moveValue = len(moveString)
        moveValue = "int@" + str(moveValue)


        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName in self.globalFrame):
                self.globalFrame[varName] = moveValue
            else:
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName in self.localFrame):
                self.localFrame[varName] = moveValue
            else:
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName in self.tempFrame):
                self.tempFrame[varName] = moveValue
            else:
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)

    def GETCHAR(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue): 
        debug.Print('Instructions: GETCHAR')
        
        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
        if(firstOpType == "var"):
            firstVal = 0
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg1, Invalid data frame")
                exit(INVALID_FRAME)
            
            try:
                firstType, firstVal = firstVal.split("@") 
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)

            
            
        if(secondOpType == "var"):
            secondVal = 0
            secondFrameType, secondVarName = secondOpValue.split("@")
            if(secondFrameType == "GF"):
                if(secondVarName in self.globalFrame):
                    secondVal = self.globalFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.localFrame):
                    secondVal = self.localFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.tempFrame):
                    secondVal = self.tempFrame.get(secondVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg2, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                secondType, secondVal = secondVal.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)

            if not (secondType == "int"):
                debug.Print("Expected int value")
                exit(WRONG_OPERANDS)

            
        if(firstOpType == "string"):
            firstVal = firstOpValue
            firstType = firstOpType
        else:
            debug.Print("Unexpected op type")
            exit(WRONG_OPERANDS)

        if(secondOpType == "int"):
            secondVal = secondOpValue
        else:
            debug.Print("expected int value")
            exit(WRONG_OPERANDS)

        length = len(firstVal)
        if(int(secondVal) > (length-1) or int(secondVal) < 0):
            debug.Print("Outside the range") 
            exit(INVALID_STRING)
        else:
            result = firstVal[int(secondVal)]  
        
        if(frameType == "GF"):
            self.globalFrame[varName] = firstType + "@" + str(result)  
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            self.localFrame[varName] = firstType + "@" + str(result)  
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            self.tempFrame[varName] = firstType + "@" + str(result)  
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)

    def SETCHAR(self, inputVarName, firstOpType, firstOpValue, secondOpType, secondOpValue):
        debug.Print('Instructions: SETCHAR')

        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName not in self.globalFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.localFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName not in self.tempFrame):
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        
        if(firstOpType == "var"):
            firstVal = 0
            firstFrameType, firstVarName = firstOpValue.split("@")
            if(firstFrameType == "GF"):
                if(firstVarName in self.globalFrame):
                    firstVal = self.globalFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.localFrame):
                    firstVal = self.localFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(firstFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstVarName in self.tempFrame):
                    firstVal = self.tempFrame.get(firstVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg1, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                firstType, firstVal = firstVal.split("@") 
            except:
                debug.Print("Wrong operands")
                exit(MISSING_VALUE)
            if not (firstType == "int"):
                debug.Print("Expected int value")
                exit(WRONG_OPERANDS)
            
            
        if(secondOpType == "var"):
            secondVal = 0
            secondFrameType, secondVarName = secondOpValue.split("@")
            if(secondFrameType == "GF"):
                if(secondVarName in self.globalFrame):
                    secondVal = self.globalFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.localFrame):
                    secondVal = self.localFrame.get(secondVarName)
                else:
                    debug.Print("Arg2, Var does not exist in current scope")
                    exit(INVALID_VAR)
            elif(secondFrameType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondVarName in self.tempFrame):
                    secondVal = self.tempFrame.get(secondVarName)
                else:
                    debug.Print("Arg1, Var does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg2, Invalid data frame")
                exit(INVALID_FRAME)
            try:
                secondType, secondVal = secondVal.split("@") 
            except:
                debug.Print("Wrong operands")
                exit(MISSING_VALUE)
            
        if(secondOpType == "string"):
            secondVal = secondOpValue
        else:
            debug.Print("Expected int value")
            exit(WRONG_OPERANDS)

        if(firstOpType == "int"):
            firstVal = firstOpValue
        else:
            debug.Print("Expected int value")
            exit(WRONG_OPERANDS)

        changeString = ""

        if(frameType == "GF"):
            changeString = self.globalFrame.get(varName)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            changeString = self.localFrame.get(varName)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            changeString = self.tempFrame.get(varName)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)
        try:
            changeType, changeValue = changeString.split("@")
        except:
            debug.Print("Missing value")
            exit(MISSING_VALUE)
        if not (changeType == "string"):
            debug.Print("Variable is not type string")
            exit(WRONG_OPERANDS)

        length = len(changeValue)
        if(int(firstVal) > (length-1) or int(firstVal) < 0):
            debug.Print("Outside the range") 
            exit(INVALID_STRING)
        else:
            if(secondVal == None):
                debug.Print("is NONE")
                exit(INVALID_STRING)
            if(len(secondVal) > 1):
                #changeValue[:int(firstVal)] = + secondVal[0] + changeValue[(int(firstVal)+1):]
                if(secondVal[0] == "\\"):
                    occurrences = self.findOccurrences(secondVal, '\\')
                    secondVal = self.returnValidString(occurrences, secondVal)
                    
                replacer = secondVal[0]
                firstPart = changeValue[:int(firstVal)]
                secondPart = changeValue[(int(firstVal) + 1):]
                changeValue = firstPart + replacer + secondPart
            else:
                replacer = secondVal
                firstPart = changeValue[:int(firstVal)]
                secondPart = changeValue[(int(firstVal) + 1):]
                changeValue = firstPart + replacer + secondPart

        if(frameType == "GF"):
            self.globalFrame[varName] = changeType + "@" + str(changeValue) 
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            self.localFrame[varName] = changeType + "@" + str(changeValue)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            self.tempFrame[varName] = changeType + "@" + str(changeValue)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)

    def TYPE(self, inputVarName, argType, inputArgValue):
        debug.Print('Instructions: TYPE')

        if(argType == "var"):
            argFrame, argValue = inputArgValue.split("@")
            if(argFrame == "GF"):
                if(argValue in self.globalFrame):
                    typeValue = self.globalFrame.get(argValue)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            elif(argFrame == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(argValue in self.localFrame):
                    typeValue = self.localFrame.get(argValue)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            elif(argFrame == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(argValue in self.tempFrame):
                    typeValue = self.tempFrame.get(argValue)
                else:
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
            else:
                debug.Print("Arg, Invalid frame")
                exit(INVALID_VAR)

        elif(argType == "int" or argType == "bool" or argType == "string" or argType == "nil"):
            typeValue = argType + "@" + inputArgValue  
        else:
            debug.Print("Invalid Argument, no var or type")
            exit(INVALID_VAR)     
        
        if(typeValue == None):
            typType = ""
        else:
            typType, typeValue = typeValue.split("@", 1)
            
        frameType, varName = inputVarName.split("@")
        if(frameType == "GF"):
            if(varName in self.globalFrame):
                self.globalFrame[varName] = "string@" + str(typType)
            else:
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "LF"):
            if(self.localFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName in self.localFrame):
                self.localFrame[varName] = "string@" + str(typType)
            else:
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        elif(frameType == "TF"):
            if(self.tempFlag == False):
                debug.Print("Frame does not exist")
                exit(INVALID_FRAME)
            if(varName in self.tempFrame):
                self.tempFrame[varName] = "string@" + str(typType)
            else:
                debug.Print("Variable does not exist in current scope")
                exit(INVALID_VAR)
        else:
            debug.Print("Invalid frame type")
            exit(INVALID_VAR)

    def LABEL(self):
        debug.Print('Instructions: LABEL')
        #self.labelStack[labelName] = order

    def NONE(self):
        debug.Print('Instructions: NONE')

    def JUMPIFEQ(self, firstOpType, firstOpValue, secondOpType, secondOpValue):
        if(firstOpType == "var"):
            firstType, firstValue = firstOpValue.split("@")
            if(firstType == "GF"):
                if(firstValue not in self.globalFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    compareOne = self.globalFrame.get(firstValue)

            elif(firstType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstValue not in self.localFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    compareOne = self.localFrame.get(firstValue)

            elif(firstType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(firstValue not in self.tempFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    compareOne = self.tempFrame.get(firstValue)

            else:
                debug.Print("Invalid frame")
                exit(WRONG_OPERANDS)

            try:
                firstOpType, firstOpValue = compareOne.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)

        if(secondOpType == "var"):
            secondType, secondValue = secondOpValue.split("@")
            if(secondType == "GF"):
                if(secondValue not in self.globalFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    compareTwo = self.globalFrame.get(secondValue)

            elif(secondType == "LF"):
                if(self.localFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondValue not in self.localFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    compareTwo = self.localFrame.get(secondValue)

            elif(secondType == "TF"):
                if(self.tempFlag == False):
                    debug.Print("Frame does not exist")
                    exit(INVALID_FRAME)
                if(secondValue not in self.tempFrame):
                    debug.Print("Variable does not exist in current scope")
                    exit(INVALID_VAR)
                else:
                    compareTwo = self.tempFrame.get(secondValue)

            else:
                debug.Print("Invalid frame")
                exit(WRONG_OPERANDS)

            try:
                secondOpType, secondOpValue = compareTwo.split("@")
            except:
                debug.Print("Variable is no type")
                exit(MISSING_VALUE)
                
        if((firstOpType == "nil" or secondOpType == "nil")):
            if(firstOpType == "nil" and secondOpType == "nil"):
                return True
            else:
                return False

        if(firstOpType == secondOpType):
            if(firstOpType == "string"):
                if(firstOpValue == None):
                    firstOpValue = ""
                else:
                    occurrences = self.findOccurrences(firstOpValue, "\\")
                    firstOpValue = self.returnValidString(occurrences, firstOpValue)
            
            if(secondOpType == "string"):
                if(secondOpValue == None):
                    secondOpValue = ""
                else:
                    occurrences = self.findOccurrences(secondOpValue, "\\")
                    secondOpValue = self.returnValidString(occurrences, secondOpValue)

            if(firstOpValue == secondOpValue):
                return True
            else:
                return False

        else:
            debug.Print("Operand types are not same type")
            exit(WRONG_OPERANDS)

        return False
        
    def EXIT(self, constType, constValue):
        debug.Print('Instructions: EXIT')
        if(constType == "int"):
            if(int(constValue) > 49 or int(constValue) < 0):
                debug.Print("Invalid Exit value")
                exit(INVALID_OPERAND_VALUE)
            else:
                exit(int(constValue))

        else:
            debug.Print("Invalid value, expected int, received something else")
            exit(WRONG_OPERANDS)

    def DPRINT(self):
        debug.Print('Instructions: DPRINT')

    def BREAK(self):
        debug.Print('Instructions: BREAK')

    # STATS
    # set of instructions that only work with dataStack
    # only difference is jumpifeq, jumpifneq, they take label as argument

    def maxVars(self):
        debug.Print("STATS - vars: counting")
        varsCounter = 0
        for g in self.globalFrame.values():
            if not (g == None):
                varsCounter += 1
        if(self.localFlag == True):
            for l in self.localFrame.values():
                if not (l == None):
                    varsCounter += 1
        if(self.tempFlag == True):
            for t in self.tempFrame.values():
                if not (t == None):
                    varsCounter += 1

        if(varsCounter > self.maxVarsCounter):
            self.maxVarsCounter = varsCounter

    def printMaxVars(self):
        return(self.maxVarsCounter)

    # STACK

    def CLEARS(self):
        debug.Print("Instructions: CLEARS")
        while(len(self.dataStack) > 0):
            self.dataStack.pop()
    
    def ADDS(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")
        secondType, secondValue = secondPar.split("@")

        if (firstType == "int" and secondType == "int"):
            result = int(firstValue) + int(secondValue)
            self.dataStack.append("int@" + str(result))
        else:    
            debug.Print("Operands are not type int")
            exit(WRONG_OPERANDS)

    def SUBS(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")
        secondType, secondValue = secondPar.split("@")

        if (firstType == "int" and secondType == "int"):
            result = int(firstValue) - int(secondValue)
            self.dataStack.append("int@" + str(result))
        else:    
            debug.Print("Operands are not type int")
            exit(WRONG_OPERANDS)

    def MULS(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")
        secondType, secondValue = secondPar.split("@")

        if (firstType == "int" and secondType == "int"):
            result = int(firstValue) * int(secondValue)
            self.dataStack.append("int@" + str(result))
        else:    
            debug.Print("Operands are not type int")
            exit(WRONG_OPERANDS)

    def IDIVS(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")
        secondType, secondValue = secondPar.split("@")

        if (firstType == "int" and secondType == "int"):
            if(int(secondValue) == 0):
                debug.Print("Division by zero")
                exit(INVALID_OPERAND_VALUE)
            else:
                result = int(firstValue) / int(secondValue)
                self.dataStack.append("int@" + str(int(float(result))))
        else:    
            debug.Print("Operands are not type int")
            exit(WRONG_OPERANDS)

    def LTS(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")
        secondType, secondValue = secondPar.split("@")

        if (not(firstType == secondType) or (firstType == "nil" or secondType == "nil")):
            debug.Print("Instructions are different types/nil")
            exit(WRONG_OPERANDS)
        else:
            if(firstType == "int"):
                firstValue = int(float(firstValue))
                secondValue = int(float(secondValue))
                if(firstValue < secondValue):
                    self.dataStack.append("bool@true")
                else:
                    self.dataStack.append("bool@false")
                
            elif(firstType == "bool"):
                if(firstValue == "false" and secondValue == "true"):
                    self.dataStack.append("bool@true")
                else:
                    self.dataStack.append("bool@false")

            else:
                if(firstType == "string"):
                    occurrences = self.findOccurrences(firstValue, '\\')
                    firstValue = self.returnValidString(occurrences, firstValue)
                if(secondType == "string"):
                    occurrences = self.findOccurrences(secondValue, '\\')
                    secondValue = self.returnValidString(occurrences, secondValue)

                if(firstValue < secondValue):
                    self.dataStack.append("bool@true")
                else:
                    self.dataStack.append("bool@false")

    def GTS(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")
        secondType, secondValue = secondPar.split("@")

        if (not(firstType == secondType) or (firstType == "nil" or secondType == "nil")):
            debug.Print("Instructions are different types/nil")
            exit(WRONG_OPERANDS)
        else:
            if(firstType == "int"):
                firstValue = int(float(firstValue))
                secondValue = int(float(secondValue))
                if(firstValue > secondValue):
                    self.dataStack.append("bool@true")
                else:
                    self.dataStack.append("bool@false")
                
            elif(firstType == "bool"):
                if(firstValue == "true" and secondValue == "false"):
                    self.dataStack.append("bool@true")
                else:
                    self.dataStack.append("bool@false")

            else:
                if(firstType == "string"):
                    occurrences = self.findOccurrences(firstValue, '\\')
                    firstValue = self.returnValidString(occurrences, firstValue)
                if(secondType == "string"):
                    occurrences = self.findOccurrences(secondValue, '\\')
                    secondValue = self.returnValidString(occurrences, secondValue)

                if(firstValue > secondValue):
                    self.dataStack.append("bool@true")
                else:
                    self.dataStack.append("bool@false")

    def EQS(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")
        secondType, secondValue = secondPar.split("@")

        if (not(firstType == secondType)):
            debug.Print("Instructions are different types/nil")
            exit(WRONG_OPERANDS)
        else:
            if(firstType == "int"):
                firstValue = int(float(firstValue))
                secondValue = int(float(secondValue))
                if(firstValue == secondValue):
                    self.dataStack.append("bool@true")
                else:
                    self.dataStack.append("bool@false")
                
            elif(firstType == "bool"):
                if((firstValue == "true" and secondValue == "true") or (firstValue == "false" and secondValue == "false")):
                    self.dataStack.append("bool@true")
                else:
                    self.dataStack.append("bool@false")

            elif(firstType == "nil" or secondType == "nil"):
                if(firstType == "nil" and secondType == "nil"):
                    self.dataStack.append("bool@true")
                else:
                    self.dataStack.append("bool@false")

            else:
                if(firstType == "string"):
                    occurrences = self.findOccurrences(firstValue, '\\')
                    firstValue = self.returnValidString(occurrences, firstValue)
                if(secondType == "string"):
                    occurrences = self.findOccurrences(secondValue, '\\')
                    secondValue = self.returnValidString(occurrences, secondValue)

                if(firstValue > secondValue):
                    self.dataStack.append("bool@true")
                else:
                    self.dataStack.append("bool@false")

    def ANDS(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")
        secondType, secondValue = secondPar.split("@")

        if (firstType == "bool" and secondType == "bool"):
            result = self.logAND(firstValue, secondValue)
            self.dataStack.append("bool@" + str(result))
        else:    
            debug.Print("Operands are not type int")
            exit(WRONG_OPERANDS)

    def ORS(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")
        secondType, secondValue = secondPar.split("@")

        if (firstType == "bool" and secondType == "bool"):
            result = self.logOR(firstValue, secondValue)
            self.dataStack.append("bool@" + str(result))
        else:    
            debug.Print("Operands are not type int")
            exit(WRONG_OPERANDS)

    def NOTS(self):
        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")

        if (firstType == "bool"):
            if(firstValue == "true"):
                self.dataStack.append("bool@false")
            elif(firstValue == "false"):
                self.dataStack.append("bool@true")
        else:    
            debug.Print("Operands are not type int")
            exit(WRONG_OPERANDS)

    def INT2CHARS(self):
        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)
        
        firstType, firstValue = firstPar.split("@")

        if(firstType == "int"):
            self.dataStack.append("string@" + (chr(int(firstValue))))
        else:
            debug.Print("Operands are not type int")
            exit(WRONG_OPERANDS)
    
    def STRI2INTS(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)
        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        firstType, firstValue = firstPar.split("@")
        secondType, secondValue = secondPar.split("@")

        if(firstType == "string"):
            replacer = firstValue
        else:
            debug.Print("Operands are not type int")
            exit(WRONG_OPERANDS)
        
        if(secondType == "int"):
            replaceNumber = secondValue
        else:
            debug.Print("Operands are not type int")
            exit(WRONG_OPERANDS)
        

        self.dataStack.append("int@" + str(ord(str((replacer[int(replaceNumber)])))))

    def getStackValues(self):
        if not (len(self.dataStack) == 0):
            secondPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)
        if not (len(self.dataStack) == 0):
            firstPar = self.dataStack.pop()
        else:
            debug.Print("Nothing to pop!")
            exit(MISSING_VALUE)

        return(firstPar, secondPar)