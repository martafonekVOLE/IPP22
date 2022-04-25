<?php

include "supportFiles/scanner.php"; 
include "supportFiles/syntax.php";
include "supportFiles/debugPrint.php";

# Allow output to STDERR
$allowLexemOutput = false;
$allowSyntaxOutput = false;

#Disable XML output
$disableXML = false;

# Read STDIN
$IN = STDIN;

# Error codes
const missingParam = 10;
const openingInError = 11;
const openingOutError = 12;
const internError = 99;
const missingHeader = 21;
const wrongOpcode = 22;
const lexsynError = 23;

# Tokens
const tokenEOF = 0;
const tokenConst = 1;
const tokenVar = 2;
const tokenHeader = 3;
const tokenOpcode = 4;
const tokenLabel = 5;
const tokenType = 6;

$amountOfComments = 0;
$amountOfLabels = 0;
$amountOfJumps = 0;

$acceptLabel = false;

$instructions = array(
    # frames, functions instructions
    0 => "MOVE",
    1 => "CREATEFRAME",
    2 => "PUSHFRAME",
    3 => "POPFRAME",
    4 => "DEFVAR",
    5 => "CALL",
    6 => "RETURN",
    # data_stack instructions
    7 => "PUSHS",
    8 => "POPS",
    # arithmetic instructions
    9 => "ADD",
    10 => "SUB",
    11 => "MUL",
    12 => "IDIV",
    13 => "LT",
    14 => "GT",
    15 => "EQ",
    16 => "AND",
    17 => "OR",
    18 => "NOT",
    19 => "INT2CHAR",
    20 => "STRI2INT",
    # in-out instructions
    21 => "READ",
    22 => "WRITE",
    # string operating instructions
    23 => "CONCAT",
    24 => "STRLEN",
    25 => "GETCHAR", 
    26 => "SETCHAR", 
    # type operating instructions
    27 => "TYPE",
    28 => "LABEL",
    29 => "JUMP",
    30 => "JUMPIFEQ",
    31 => "JUMPIFNEQ",
    32 => "EXIT",
    # debugging instructions
    33 => "DPRINT",
    34 => "BREAK"
    );

# Arrays of Opcodes based on amount of operands
$noOperandInst = array(1, 2, 3, 6, 34);
$oneOperandInst = array(4, 5, 7, 8, 22, 28, 29, 32, 33);
    $getsVar = array(4, 8);
    $getsLabel = array(5, 28, 29);
$twoOperandInst = array(0, 18, 19, 21, 24, 27);
    $getsVarSymb = array(0, 18, 19, 24, 27);
$threeOperandInst = array(9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 23, 25, 26, 30, 31);
    $getsVarSymbSymb = array(9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 23, 25, 26);

# main

checkSyntax($argc);
exit(0);
?>