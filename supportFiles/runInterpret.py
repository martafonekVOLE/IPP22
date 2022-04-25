from supportFiles.exitCodes import *
from supportFiles import debug, instructions
import re, sys
import xml.etree.ElementTree as ET

class Interpret:
    "Main Interpret class"

    def __init__(self):
        debug.Print("runInterpret.py: Constructor Invoked!")

    def run(self, argv):
        debug.Print("runInterpret.py: Interpret is running!")

        # Zpracování argumentů
        if(len(argv) < 2):
            debug.Print("runInterpret.py: Invalid amount of arguments")
            exit(MISSING_PARAM)
        else:
            self.checkSource = 0
            self.checkInput = 0
            self.checkStats = False
            self.insts = False
            self.hot = False
            self.vars = False
            self.statsOrder = []
            self.openStats = ""

            argv.pop(0)


        # Arguments parsing
            for each in argv:
                if(each == "--help" and len(argv) == 1):
                    self.help()
                    debug.Print("runInterpret.py: Help called")
                    exit(0)
                elif(re.match("^--source=", each) and self.checkSource == 0):
                    self.checkSource = 1
                    _, self.openSource =  each.split("=") 
                elif(re.match("^--input=", each) and self.checkInput == 0):
                    self.checkInput = 1
                    _, self.openInput = each.split("=")
                elif(re.match("^--stats=", each)):
                    self.checkStats = True
                    _, self.openStats = each.split("=")
                elif(re.match("^--insts$", each)):
                    self.insts = True
                    self.statsOrder.append("insts")
                elif(re.match("^--hot$", each)):
                    self.hot = True 
                    self.statsOrder.append("hot")
                elif(re.match("^--vars$", each)):
                    self.statsOrder.append("vars")
                    self.vars = True
                
                else:
                    debug.Print("runInterpret.py: Invalid parameter")
                    exit(MISSING_PARAM)

                if((self.insts == True or self.hot == True or self.vars == True) and self.checkStats == False):
                    debug.Print("Expected parameter stats")
                    exit(MISSING_PARAM)


    # Input files parsing
            if((self.checkSource + self.checkInput) < 1):
                debug.Print("runInterpret.py: Missing parameter source or input")
                exit(MISSING_PARAM)
            
            # check if source exists
            if(self.checkSource == 1):
                try:
                    with open(self.openSource) as os:
                        self.sourceLines = os.readlines()
                except:
                    debug.Print("runInterpret.py: Specified file does not exist")
                    exit(OPENING_IN_ERROR)
            else:
                self.sourceLines = []
                for line in sys.stdin:
                    self.sourceLines.append(line)

            # check if input exists
            if(self.checkInput == 1): 
                try:
                    with open(self.openInput) as oi:
                        self.inputLines = oi.readlines()
                except:
                    debug.Print("runInterpret.py: Specified file does not exist")
                    exit(OPENING_IN_ERROR)
            else:
                debug.Print("runInterpret.py: Input not given, expected on STDIN") 
        
        try:
            self.xmlForm = self.parseXML(self.sourceLines)
            self.root = ET.fromstring(self.xmlForm) 
        except: 
            debug.Print("runInterpret.py: Wrong XML structure")
            exit(INVALID_IN_XML)

        return(self.root, self.checkStats, self.insts, self.hot, self.vars, self.statsOrder, self.openStats)


    # parsing XML
    def parseXML(self, lines):
        debug.Print("parseXML: Parsing started")
        string = ""
        for line in lines:
            string += line
        
        return(string)

    # returns input lines, if --input was used
    def getInput(self):
        return(self.inputLines)

    # handles source and input
    def sourceInputHandler(self):
        if(self.checkInput == 1 and self.checkSource == 1):
            return(2)
        elif(self.checkInput == 1 and self.checkSource == 0):
            return(1)
        else:
            return(-1)
    
    # Prints help prompt
    def help(self):
        print("---------------------")
        print("INTERPRET.PY")
        print("Author: Martin Pech (xpechm00)")
        print("---------------------")
        print("This script is used for interpretation of the unstructured imperative language IPPcode22")
        print("---------------------")
        print("Usage:")
        print("\t--help -> Prints this prompt")
        print("\t--source=file -> XML file input")
        print("\t--input=file -> file with inputs for XML") 
        print("---------------------\n")

# Class responsible for XML magic
class XmlManager:
    def __init__(self, root, lines=[], checkStats = False, insts = False, hot = False, svars = False, statsOrder = [], openStats = ""):
        debug.Print("XmlManager: Started")
        
        # STATS
        self.checkStats = checkStats
        self.insts = insts
        self.hot = hot
        self.vars = svars
        self.statsOrder = statsOrder
        self.openStats = openStats
        self.allOrders = {}

        self.instsVal = 0

        # used for valid amount of arguments check
        self.zeroArg = "CREATEFRAME PUSHFRAME POPFRAME RETURN BREAK CLEARS ADDS SUBS MULS IDIVS LTS GTS EQS ANDS ORS NOTS INT2CHARS STRI2INTS" 
        self.oneArg = "DEFVAR CALL PUSHS POPS WRITE LABEL JUMP EXIT DPRINT JUMPIFEQS JUMPIFNEQS"
        self.twoArg = "MOVE INT2CHAR READ TYPE STRLEN NOT"
        self.threeArg = "ADD SUB MUL IDIV LT GT EQ AND OR STRI2INT CONCAT GETCHAR SETCHAR JUMPIFEQ JUMPIFNEQ"

        # other control and usefull variables/...
        self.lines = lines
        self.lines.reverse()

        self.checkDuplicit = []
        self.implicitOrder = 0

        self.jumpFlag = False
    
        self.root = root
        self.labelsRoot = root
        self.controlOrder = 0

        if(self.root.tag != "program"):
            debug.Print("XmlManager: Invalid root tag!")
            exit(INVALID_XML_STRUCTURE)
        #not re.match("^ippcode22$", list(self.root.attrib.tag())[0], re.IGNORECASE)

        countI = 0
        tokenl = False

        # checking root element attributes validity
        for ra in (list(self.root.attrib)):
            if not (ra == "language" or ra == "name" or ra == "description"):
                debug.Print("XmlManager: Invalid attribute in root tag")
                exit(INVALID_XML_STRUCTURE)
            else:
                if(ra == "language"):
                    tokenl = True
                    if(not re.match("^ippcode22$", list(self.root.attrib.values())[countI], re.IGNORECASE)):
                        debug.Print("XmlManager: Invalid language")
                        exit(INVALID_XML_STRUCTURE)

            countI += 1
        
        if(tokenl == False):
            debug.Print("XmlManager: Root tag is missing attribute language")


        self.amountOfChildren = 0
        self.stop = 0

        self.labels = {}
        self.returns = []

        self.tokenExit = True

        self.frame = instructions.Depth()

        for child in self.root:
            self.amountOfChildren += 1

    # returns amount of root's children
    def children(self):
        return self.amountOfChildren

    # checking if labels are correct, putting them into array
    def checkLabels(self):
        for label in self.labelsRoot:
            # Checking if order is valid
            # if order is number
            try:
                if(not re.match("^[0-9]+$", (list(label.attrib.values())[0]))):
                    debug.Print("Invalid order type")
                    exit(INVALID_XML_STRUCTURE)

            except:
                debug.Print("Invalid element")
                exit(INVALID_XML_STRUCTURE)

            # if order is uniqe is source
            if((int(list(label.attrib.values())[0]) in self.checkDuplicit) or int(list(label.attrib.values())[0]) < 0):
                debug.Print("This instruction order already exists")
                exit(INVALID_XML_STRUCTURE)
            else:
                self.checkDuplicit.append(int(list(label.attrib.values())[0])) #int
                self.implicitOrder += 1


            # Check childeren elements
            labelsArr = []
            for l in label:
                labelsArr.append(l)
                
                # Missing Opcode or number
                try:
                    checkOpcode = (list(label.attrib.values())[1])
                    checkOpnumber = (list(label.attrib.values())[0])
                except:
                    debug.Print("Missing opcode or number")
                    exit(INVALID_XML_STRUCTURE)

            # Checking label
            if re.match('^LABEL$', (list(label.attrib.values())[1]), re.IGNORECASE):
                if(labelsArr[0].text in self.labels):
                    debug.Print("Label already exists")
                    exit(SEMANTICK_ERROR)
                else:
                    self.labels[labelsArr[0].text] = self.implicitOrder 


    # this method handles actual instruction
    # it also handles order of instruction in which they are processed
    def getNext(self):
        self.checkDuplicit.sort()
        
        # Determines which instruction is being processed
        for child in self.root:
            self.actualChild = child
            try:
                if (int(list(self.actualChild.attrib.values())[0]) == int(self.checkDuplicit[self.stop])):
                    break
            except:
                self.ManageStats()
                exit(0)

        self.stop +=1
        try:
            if(self.actualChild.tag):
                _ = self.tokenExit
        except:
            self.ManageStats()
            exit(0)

        if not (self.actualChild.tag == "instruction"):
            debug.Print("Invalid tag instruction")
            exit(INVALID_XML_STRUCTURE)
        
        if not (len(list(self.actualChild.attrib)) == 2):
            debug.Print("Instruction does have invalid amount of arguments")
            exit(INVALID_XML_STRUCTURE)
        else:
            for a in list(self.actualChild.attrib):
                if not (a == "order" or a == "opcode"):
                    debug.Print("Instruction requires order, opcode")
                    exit(INVALID_XML_STRUCTURE)

        # checking instruction unique order
        if(int(list(self.actualChild.attrib.values())[0]) in self.checkDuplicit):
            if(int(self.controlOrder) >= int(list(self.actualChild.attrib.values())[0])): #-> Controling if instructions are in ascending order
                if(int(self.controlOrder) == int(list(self.actualChild.attrib.values())[0]) and self.jumpFlag == False and int(self.checkDuplicit.pop()) == int(list(self.actualChild.attrib.values())[0])):
                    self.ManageStats()
                    exit(0)
                elif(self.jumpFlag == False):
                    debug.Print("XmlManager: Invalid order!")
                    exit(INVALID_XML_STRUCTURE)
                
        else:
            debug.Print("XmlManager: Unexpected order number")
            exit(INVALID_IN_XML)

        # STATS
        if((list(self.actualChild.attrib.values())[0]) in self.allOrders):
            increment = self.allOrders.get((list(self.actualChild.attrib.values())[0]))
            increment = int(increment)
            increment += 1
            self.allOrders[(list(self.actualChild.attrib.values())[0])] = increment
        else:
            self.allOrders[(list(self.actualChild.attrib.values())[0])] = 1

        # Kontrola poradi instrukci
        # if(int(list(self.actualChild.attrib.values())[0]) <= int(self.controlOrder)):
        #     checkCorrect = self.children()
            
        #     if(self.controlOrder == int(list(self.actualChild.attrib.values())[0])):
        #         debug.Print("End of source file")
        #         exit(0)
                
        #     else:
        #         if(self.jumpFlag == False):
        #             debug.Print("XmlManager: Invalid order!")
        #             exit(INVALID_IN_XML)


        self.controlOrder = self.stop
        self.jumpFlag = False

        # Zavedeni argumentu do list
        self.argumentsArr = []
        self.checkArguments = []
        for ch in self.actualChild:
            if(not re.match('^arg[1-3]$', ch.tag, re.IGNORECASE)):
                debug.Print("Invalid argument tag")
                exit(INVALID_XML_STRUCTURE)
            else:
                for at in list(ch.attrib):
                    if not (at == "type"):
                        debug.Print("Argument requires attribute type")
                        exit(INVALID_XML_STRUCTURE)
                        
                _, argCheck = ch.tag.split("g")
                if argCheck not in self.checkArguments:
                    self.checkArguments.append(argCheck)
                else:
                    exit(INVALID_XML_STRUCTURE)

        # valid amount of arguments checking
        if(("2" in self.checkArguments and "1" not in self.checkArguments)):
            debug.Print("Invalid argument number")
            exit(INVALID_XML_STRUCTURE)
        if(("3" in self.checkArguments and ("1" not in self.checkArguments or "2" not in self.checkArguments))):
            exit(INVALID_XML_STRUCTURE)
        
        arg1 = 0
        arg2 = 0
        arg3 = 0
        tokenArg1 = False
        tokenArg2 = False
        tokenArg3 = False
        for ch in self.actualChild:
            _, argCheck = ch.tag.split("g")
            if(argCheck == "1" and tokenArg1 == False):
                arg1 = ch
                tokenArg1 = True
            elif(argCheck == "2" and tokenArg2 == False):
                arg2 = ch
                tokenArg2 = True
            else:
                tokenArg3 = True
                arg3 = ch

        if(tokenArg1 == True):
            self.argumentsArr.append(arg1)
        if(tokenArg2 == True):
            self.argumentsArr.append(arg2)
        if(tokenArg3 == True):
            self.argumentsArr.append(arg3)
        
        if(len(self.argumentsArr) == 0):
            if((list(self.actualChild.attrib.values())[1]).upper() not in self.zeroArg):
                debug.Print("Invalid number of arguments for this instruction: " + list(self.actualChild.attrib.values())[1])
                exit(INVALID_XML_STRUCTURE)
        elif(len(self.argumentsArr) == 1):
            if((list(self.actualChild.attrib.values())[1]).upper() not in self.oneArg):
                debug.Print("Invalid number of arguments for this instruction: " + list(self.actualChild.attrib.values())[1])
                exit(INVALID_XML_STRUCTURE)
        elif(len(self.argumentsArr) == 2):
            if((list(self.actualChild.attrib.values())[1]).upper() not in self.twoArg):
                debug.Print("Invalid number of arguments for this instruction: " + list(self.actualChild.attrib.values())[1])
                exit(INVALID_XML_STRUCTURE)
        else:
            if((list(self.actualChild.attrib.values())[1]).upper() not in self.threeArg):
                debug.Print("Invalid number of arguments for this instruction: " + list(self.actualChild.attrib.values())[1])
                exit(INVALID_XML_STRUCTURE)
    
        # -> prints 'GF@a' print((self.argumentsArr[0].text))
        # -> prints value (order = 12) print(list(self.actualChild.attrib.values())[1])

        # Individual instructions handling
        if re.match('^MOVE$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
	        self.frame.MOVE(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text)

        elif re.match('^CREATEFRAME$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.CREATEFRAME()    

        elif re.match('^PUSHFRAME$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.PUSHFRAME()      
            
        elif re.match('^POPFRAME$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.POPFRAME()       

        elif re.match('^DEFVAR$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.DEFVAR(self.argumentsArr[0].text)   

        elif re.match('^CALL$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.CALL()
            if(self.argumentsArr[0].text in self.labels):
                order = int(list(self.actualChild.attrib.values())[0])

                order = self.checkDuplicit.index((order))

                self.stop = int(self.labels.get(self.argumentsArr[0].text))

                self.returns.append((order + 1)) 
                self.jumpFlag = True

            else:
                debug.Print("Requested Label does not exist")
                exit(SEMANTICK_ERROR) 
                
        elif re.match('^RETURN$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            debug.Print("Instructions: RETURN")
            try:
                order = int(self.returns.pop())
                self.jumpFlag = True

            except:
                debug.Print("Return stack is empty")
                exit(MISSING_VALUE)

            self.stop = int(order)
            self.controlOrder = int(order) - 1

        elif re.match('^PUSHS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.PUSHS(self.argumentsArr[0].text, list(self.argumentsArr[0].attrib.values())[0])

        elif re.match('^POPS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.POPS(self.argumentsArr[0].text)

        elif re.match('^ADD$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.ADD(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^SUB$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.SUB(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^MUL$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.MUL(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^IDIV$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.IDIV(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^LT$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.LT(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^GT$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.GT(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^EQ$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.EQ(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^AND$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.AND(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^OR$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.OR(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^NOT$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.NOT(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text)

        elif re.match('^INT2CHAR$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.INT2CHAR(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text)

        elif re.match('^STRI2INT$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.STRI2INT(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^READ$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            if(len(self.lines) != 0):
                line = self.lines.pop()
            else:
                line = ""
                
            self.frame.READ(self.argumentsArr[0].text, self.argumentsArr[1].text, line)

        elif re.match('^WRITE$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.WRITE(list(self.argumentsArr[0].attrib.values())[0], self.argumentsArr[0].text)

        elif re.match('^CONCAT$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.CONCAT(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^STRLEN$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.STRLEN(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text)

        elif re.match('^GETCHAR$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.GETCHAR(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^SETCHAR$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.SETCHAR(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)

        elif re.match('^TYPE$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.TYPE(self.argumentsArr[0].text, list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text)

        elif re.match('^LABEL$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            self.frame.NONE()

        elif re.match('^JUMP$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            debug.Print("Instructions: JUMP")
            if(self.argumentsArr[0].text in self.labels):
                order = self.labels.get(self.argumentsArr[0].text)
                self.stop = int(order)
                self.jumpFlag = True

            else:
                debug.Print("Requested Label does not exist")
                exit(SEMANTICK_ERROR)

        elif re.match('^JUMPIFEQ$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            debug.Print("Instructions: JUMPIFEQ")
            checkJump = self.frame.JUMPIFEQ(list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)
            if(checkJump):
                if(self.argumentsArr[0].text in self.labels):
                    order = self.labels.get(self.argumentsArr[0].text)
                    self.stop = int(order)
                    self.jumpFlag = True

                else:
                    debug.Print("Requested Label does not exist")
                    exit(SEMANTICK_ERROR)
            else:
                debug.Print("not jumping")
                if not(self.argumentsArr[0].text in self.labels):
                    debug.Print("Requested Label does not exist")
                    exit(SEMANTICK_ERROR)

        elif re.match('^JUMPIFNEQ$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            debug.Print("Instructions: JUMPIFEQ")
            checkJump = self.frame.JUMPIFEQ(list(self.argumentsArr[1].attrib.values())[0], self.argumentsArr[1].text, list(self.argumentsArr[2].attrib.values())[0], self.argumentsArr[2].text)
            if(not checkJump):
                if(self.argumentsArr[0].text in self.labels):
                    order = self.labels.get(self.argumentsArr[0].text)
                    self.stop = int(order)
                    self.jumpFlag = True

                else:
                    debug.Print("Requested Label does not exist")
                    exit(SEMANTICK_ERROR)
            else:
                debug.Print("not jumping")
                if not(self.argumentsArr[0].text in self.labels):
                    debug.Print("Requested Label does not exist")
                    exit(SEMANTICK_ERROR)

        elif re.match('^EXIT$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE): #done
            #self.frame.EXIT(list(self.argumentsArr[0].attrib.values())[0], self.argumentsArr[0].text)
            self.ManageStats()

            debug.Print('Instructions: EXIT')
            if(list(self.argumentsArr[0].attrib.values())[0] == "int"):
                if(int(self.argumentsArr[0].text) > 49 or int(self.argumentsArr[0].text) < 0):
                    debug.Print("Invalid Exit value")
                    exit(INVALID_OPERAND_VALUE)
                else:
                    exit(int(self.argumentsArr[0].text))
            else:
                debug.Print("Invalid value, expected int, received something else")
                exit(WRONG_OPERANDS)



        elif re.match('^DPRINT$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.DPRINT() #funkce Dprint() v debugu

        elif re.match('^BREAK$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.BREAK()
        
        # STACK
        elif re.match('^CLEARS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.CLEARS()

        elif re.match('^ADDS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.ADDS()

        elif re.match('^SUBS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.SUBS()

        elif re.match('^MULS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.MULS()

        elif re.match('^IDIVS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.IDIVS()

        elif re.match('^LTS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.LTS()

        elif re.match('^GTS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.GTS()

        elif re.match('^EQS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.EQS()

        elif re.match('^ANDS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.ANDS()

        elif re.match('^ORS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.ORS()

        elif re.match('^NOTS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.NOTS()

        elif re.match('^INT2CHARS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.INT2CHARS()

        elif re.match('^STRI2INTS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            self.frame.STRI2INTS()

        elif re.match('^JUMPIFEQS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):

            firstPar, secondPar = self.frame.getStackValues()

            firstType, firstValue = firstPar.split("@")
            secondType, secondValue = secondPar.split("@")

            if not (firstType == secondType):
                debug.Print("Operands are not type int")
                exit(WRONG_OPERANDS)

            if(firstValue == secondValue):
                if(self.argumentsArr[0].text in self.labels):
                    order = self.labels.get(self.argumentsArr[0].text)
                    self.stop = int(order)
                    self.jumpFlag = True
                else:
                    debug.Print("Requested Label does not exist")
                    exit(SEMANTICK_ERROR)
            else:
                debug.Print("not jumping")
                if not(self.argumentsArr[0].text in self.labels):
                    debug.Print("Requested Label does not exist")
                    exit(SEMANTICK_ERROR)



        elif re.match('^JUMPIFNEQS$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE):
            firstPar, secondPar = self.frame.getStackValues()

            firstType, firstValue = firstPar.split("@")
            secondType, secondValue = secondPar.split("@")

            if not (firstType == secondType):
                debug.Print("Operands are not type int")
                exit(WRONG_OPERANDS)

            if not (firstValue == secondValue):
                if(self.argumentsArr[0].text in self.labels):
                    order = self.labels.get(self.argumentsArr[0].text)
                    self.stop = int(order)
                    self.jumpFlag = True
                else:
                    debug.Print("Requested Label does not exist")
                    exit(SEMANTICK_ERROR)
            else:
                debug.Print("not jumping")
                if not(self.argumentsArr[0].text in self.labels):
                    debug.Print("Requested Label does not exist")
                    exit(SEMANTICK_ERROR)

        else:
            debug.Print("XmlManager: Invalid Opcode!")
            exit(INVALID_XML_STRUCTURE)

        if(re.match('^BREAK$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE) or re.match('^DPRINT$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE) or re.match('^LABEL$', (list(self.actualChild.attrib.values())[1]), re.IGNORECASE)):
            debug.Print("STATS - insts: not counting")
        else:
            self.frame.maxVars()
            debug.Print("STATS - insts: counting")
            self.instsVal += 1


    def ManageStats(self):
        if(self.checkStats == True and (self.insts == True or self.hot == True or self.vars == True)):
            f = open(self.openStats, "w")
            for each in self.statsOrder:
                if(each == "insts"):
                    f.write(str(self.instsVal) + "\n")
                elif(each == "vars"):
                    debug.Print("Printing Vars")
                    varsNum = self.frame.printMaxVars()
                    f.write(str(varsNum) + "\n")
                elif(each == "hot"):
                    debug.Print("Printing Hots")
                    test = max(self.allOrders, key=self.allOrders.get)
                    f.write(str(test) + "\n")

        else:
            debug.Print("StatsManager: Nothing to manage")