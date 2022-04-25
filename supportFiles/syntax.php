<?php
    function checkSyntax($argc){
        # global variables
        global $disableXML;     # disables XML output -> used while debugging 
        global $instructions;   # array of all supported instructions - in parse.php

        # arrays of different amount of operands
        global $noOperandInst; 
        global $oneOperandInst; 
            global $getsVar;
            global $getsLabel;
        global $twoOperandInst;
            global $getsVarSymb;
        global $threeOperandInst;
            global $getsVarSymbSymb;

        # global counters for bonus statp
        global $amountOfComments;
        global $amountOfJumps;
        global $amountOfLabels;
        $amountOfInst = 0;
        $amountOfBadJumps = 0;

        # other variables used for statp
        $isBonus = false;
        $isFile = false;
        $isHelp = false;
        $stats = "";
        $listOfBonuses = array();
        $statFiles = array();
        $uniqueLabels = array();
        $jumpedBadLabels = array();
        $fwjumps = 0;
        $possiblyFwJump = array();
        $backjumps = 0;

        # counter - flag of context
        $dualHeader = 0;

#===============================================================
                      # XML setup
#===============================================================
        # setupXML();
        $xml = new DOMDocument();
        $xml->encoding = 'UTF-8';
        $xml->xmlVersion = '1.0';
        $xml->formatOutput = true;

        $xmlMain = $xml->createElement("program");
        $xmlMain->setAttribute("language", "IPPcode22");
        $xmlMain = $xml->appendChild($xmlMain);

#===============================================================
                    #Statp arguments
#===============================================================
        if($argc > 1){
            global $argv;
            foreach($argv as $argvKey => $arg){
                if(preg_match("/^--stats=/", $arg)){
                    $isFile = true;
                    $temp = explode("=", $arg);
                    array_push($listOfBonuses, array($argvKey, $temp[0], $temp[1]));
                }
                else if($arg == "--loc"){
                    $isBonus = true;
                    array_push($listOfBonuses, array($argvKey, "--loc"));
                }
                else if($arg == "--comments"){
                    $isBonus = true;
                    array_push($listOfBonuses, array($argvKey, "--comments"));
                }
                else if($arg == "--labels"){
                    $isBonus = true;
                    array_push($listOfBonuses, array($argvKey, "--labels"));
                }
                else if($arg == "--jumps"){
                    $isBonus = true;
                    array_push($listOfBonuses, array($argvKey, "--jumps"));
                }
                else if($arg == "--badjumps"){
                    $isBonus = true;
                    array_push($listOfBonuses, array($argvKey, "--badjumps"));
                }
                else if($arg == "--fwjumps"){
                    $isBonus = true;
                    array_push($listOfBonuses, array($argvKey, "--fwjumps"));
                }
                else if($arg == "--backjumps"){
                    $isBonus = true;
                    array_push($listOfBonuses, array($argvKey, "--backjumps"));
                }
                else if($arg == "--help"){     
                    if($argc > 2){      # cannot be combined
                        exit(10);
                    } 
                    print_help();
                    exit(0);
                }
                else if($arg == "parse.php"){

                }
                else{
                    print_Ds("Syntax: Error - unexpected/wrong input parameter");
                    exit(missingParam);
                }
            }
            if($isBonus != $isFile){
                if($isFile == false){
                    print_Ds("Syntax: Error - invalid combination of arguments");
                    exit(missingParam);
                }
            }
            if($isHelp == true && ($isBonus == true || $isFile == true)){
                exit(missingParam);
            }

        }

#===============================================================
                      # Parser started
#===============================================================
        print_Ds("\nSyntax: Requesting Token");
        $readLine = scan();

#===============================================================
                # Checking correct header
#===============================================================
        if($readLine[0][0] != tokenHeader){
            print_Ds("Syntax: Invalid/Missing Header");
            exit(missingHeader);
        }
        else{
            print_Ds("Syntax: Valid Header");
            $dualHeader = 1;
        }

#===============================================================
                # Looping through input
#===============================================================
        while(true){
            print_Ds("\nSyntax: Requesting Token");
            $readLine = scan();

            if($readLine[0][0] == tokenHeader && $dualHeader == 1){
                print_Ds("Syntax: Invalid - more headers");
                exit(wrongOpcode);
            }
            
            # is EOF
            if($readLine[0][0] == tokenEOF){
                print_Ds("Syntax: EOF");

                    # STATP
                    if(($isFile == $isBonus) && (count($listOfBonuses) != 0)){
                        $intoFile = "";
                        foreach($listOfBonuses as $lob){
                            if($lob[1] == "--stats"){
                                if($intoFile == ""){
                                    $intoFile = $lob[2];
                                }
                                else{                                                                   
                                    if($intoFile != ""){
                                        fwrite(fopen($intoFile, "w"), $stats);
                                        if($intoFile != "" && !in_array($intoFile, $statFiles)){
                                            fwrite(fopen($intoFile, "w"), $stats);
                                            $stats = "";
                                            array_push($statFiles, $intoFile);
                                        }
                                        else{
                                            if($intoFile == ""){
                                                exit(missingParam);
                                            }
                                            else{
                                                exit(openingOutError);
                                            }
                                        }
                                    }
                                    $intoFile = $lob[2];
                                }
                            }
                            if($lob[1] == "--jumps"){                   
                                $stats .= ($amountOfJumps . "\n"); 
                            }
                            if($lob[1] == "--loc"){
                                $stats .= ($amountOfInst . "\n");
                            }
                            if($lob[1] == "--comments"){
                                $stats .= ($amountOfComments . "\n");
                            }
                            if($lob[1] == "--labels"){
                                $stats .= ($amountOfLabels . "\n");
                            }
                            if($lob[1] == "--badjumps"){                    
                                foreach($jumpedBadLabels as $jbl){
                                    if(in_array($jbl, $uniqueLabels) || in_array(($jbl."\n"), $uniqueLabels)){     #failuje to, když je na konci souboru jump. WHY? eof?
                                    }
                                    else{
                                        $amountOfBadJumps++;
                                    }
                                }
                                $stats .= ($amountOfBadJumps . "\n");
                            }
                            if($lob[1] == "--backjumps"){
                                $stats .= ($backjumps . "\n");
                            }
                            if($lob[1] == "--fwjumps"){
                                foreach($possiblyFwJump as $pfj){
                                    if(in_array($pfj, $uniqueLabels) || in_array(($pfj . "\n"), $uniqueLabels)){
                                        $fwjumps++;
                                    }
                                }
                                $stats .= ($fwjumps . "\n");
                            }
                            if(count($listOfBonuses) == $lob[0]){
                                if($intoFile != "" && !in_array($intoFile, $statFiles)){
                                    fwrite(fopen($intoFile, "w"), $stats);
                                    $stats = "";
                                    array_push($statFiles, $intoFile);
                                }
                                else{
                                    if($intoFile == ""){
                                        exit(missingParam);
                                    }
                                    else{
                                        exit(openingOutError);
                                    }
                                }
                            }
                        }
                    }
                    # create empty file
                    else if($isFile == true && $isBonus == false){
                        fwrite(fopen($listOfBonuses[0][2], "w"), $stats);
                    }
                break;
            }

#===============================================================
                        # Is opcode
#===============================================================
            else if($readLine[0][0] == tokenOpcode){
                $amountOfInst++;
                print_Ds("Syntax: Opcode");

                $xmlInst = $xml->createElement("instruction");
                $xmlInst->setAttribute("order", $amountOfInst);
                $xmlInst->setAttribute("opcode", $instructions[$readLine[0][1]]);

#===============================================================
                # No operand instruction
#===============================================================
                if(in_array($readLine[0][1], $noOperandInst)){
                    print_Ds("Syntax: Found no operand instruction");

                    if(count($readLine) != 1){
                        print_Ds("Syntax: Error in no operand instruction -> wrong amount of operands");
                        exit(lexsynError);
                    }


                    print_Ds("Syntax: Success");
                }

#===============================================================
                # One operand instruction
#===============================================================
                else if(in_array($readLine[0][1], $oneOperandInst)){

                    print_Ds("Syntax: Found one operand instruction");
                    if (count($readLine) != 2){
                        print_Ds("Syntax: Error in one operand instruction -> wrong amount of operands");
                        exit(lexsynError);
                    }

                    # is DEFVAR or POPS
                    if(in_array($readLine[0][1], $getsVar)){
                        if($readLine[1][0] == tokenVar){
                            print_Ds("Syntax: Success - DEFVAR/POPS");

                            $xml1 = $xml->createElement("arg1", htmlspecialchars($readLine[1][1] . "@" . $readLine[1][2]));
                            $xml1->setAttribute("type", "var");
                            $xmlInst->appendChild($xml1);
                        }
                        else{
                            print_Ds("Syntax: Fail - DEFVAR/POPS expected tokenVar, but received something else.");
                            exit(lexsynError);
                        }
                    }

                    # is CALL, LABEL, JUMP
                    else if(in_array($readLine[0][1], $getsLabel)){
                        if($readLine[1][0] == tokenLabel){
                            print_Ds("Syntax: Success - LABEL/CALL/JUMP");
                            $xml1 = $xml->createElement("arg1", htmlspecialchars($readLine[1][1]));
                            $xml1->setAttribute("type", "label");
                            $xmlInst->appendChild($xml1);


                            # STATPP
                            if($readLine[0][1] == 28){
                                if(!in_array($readLine[1][1], $uniqueLabels)){
                                    array_push($uniqueLabels, $readLine[1][1]);
                                }
                            }
                            if($readLine[0][1] == 29 || $readLine[0][1] == 5){
                                array_push($jumpedBadLabels, $readLine[1][1]);

                                # Backjumps -> label already exists
                                if(in_array($readLine[1][1], $uniqueLabels) || in_array(($readLine[1][1] . "\n"), $uniqueLabels)){
                                    $backjumps++;
                                }        #RETURN řešit, nebo ne? #zužitkovat badjumps? stejný systém
                                # Possible forwardjump or badjump
                                else{
                                    array_push($possiblyFwJump, $readLine[1][1]);
                                }
                            }
                        }
                        else{
                            print_Ds("Syntax: Fail - LABEL/CALL/JUMP expected tokenLabel, but received something else.");
                            exit(lexsynError);
                        }
                    }

                    # is EVERYTHING ELSE - takes symb
                    else{
                        if($readLine[1][0] == tokenVar || $readLine[1][0] == tokenConst){
                            print_Ds("Syntax: Success");
                            if($readLine[1][0] == tokenVar){
                                $xml1 = $xml->createElement("arg1", htmlspecialchars($readLine[1][1] . "@" . $readLine[1][2]));
                                $xml1->setAttribute("type", "var");   
                            }
                            else{
                                $xml1 = $xml->createElement("arg1", htmlspecialchars($readLine[1][2]));
                                $xml1->setAttribute("type", $readLine[1][1]);
                            }
                            $xmlInst->appendChild($xml1);
                        }
                        else{
                            print_Ds("Syntax: Fail - Expected Symb, but received something else");
                            exit(lexsynError);
                        }
                    } 
                }

#===============================================================
                # Two operand instruction
#===============================================================
                else if(in_array($readLine[0][1], $twoOperandInst)){

                    print_Ds("Syntax: Found two operands instruction");
                    if (count($readLine) != 3){
                        print_Ds("Syntax: Error in two operands instruction -> wrong amount of operands");
                        exit(lexsynError);
                    }

                    # is EVERYTHING apart from READ
                    if(in_array($readLine[0][1], $getsVarSymb)){

                        if($readLine[1][0] == tokenVar && ($readLine[2][0] == tokenVar || $readLine[2][0] == tokenConst)){
                            print_Ds("Syntax: Success - var, var/const");
                            $xml1 = $xml->createElement("arg1", htmlspecialchars($readLine[1][1] . "@" . $readLine[1][2]));
                            $xml1->setAttribute("type", "var");
                            if($readLine[2][0] == tokenVar){
                                $xml2 = $xml->createElement("arg2", htmlspecialchars($readLine[2][1] . "@" .$readLine[2][2]));
                                $xml2->setAttribute("type", "var");
                            }
                            else{
                                $xml2 = $xml->createElement("arg2", htmlspecialchars($readLine[2][2]));
                                $xml2->setAttribute("type", $readLine[2][1]);
                            }
                            $xmlInst->appendChild($xml1);
                            $xmlInst->appendChild($xml2);

                        }
                        else{
                            print_Ds("Syntax: Fail - Expected two operands with var and var/symb");
                            exit(lexsynError);
                        }

                    }
                    # READ
                    else{
                        if($readLine[1][0] == tokenVar && $readLine[2][0] == tokenType){
                            print_Ds("Syntax: Success - READ");
                            $xml1 = $xml->createElement("arg1", htmlspecialchars($readLine[1][1] . "@" . $readLine[1][2]));
                            $xml1->setAttribute("type", "var");

                            $xml2 = $xml->createElement("arg2", htmlspecialchars($readLine[2][1]));
                            $xml2->setAttribute("type", "type");

                            $xmlInst->appendChild($xml1);
                            $xmlInst->appendChild($xml2);
                        }
                        else{
                            print_Ds("Syntax: Fail - READ got unexpected operands");
                            exit(lexsynError);
                        }
                    }
                }

#===============================================================
                # Three operand instruction
#===============================================================
                else if(in_array($readLine[0][1], $threeOperandInst)){

                    print_Ds("Syntax: Found three operands instruction");

                    if (count($readLine) != 4){
                        print_Ds("Syntax: Error in three operands instruction -> wrong amount of operands");
                        exit(lexsynError);
                    }
                    
                    if(in_array($readLine[0][1], $getsVarSymbSymb)){

                        # Var, Var/Const, Var/Const
                        if($readLine[1][0] == tokenVar && ($readLine[2][0] == tokenVar || $readLine[2][0] == tokenConst) && ($readLine[3][0] == tokenVar || $readLine[3][0] == tokenConst)){
                            print_Ds("Syntax: Success - var, var/const, var/const");
                            $xml1 = $xml->createElement("arg1", htmlspecialchars($readLine[1][1] . "@" . $readLine[1][2]));
                            $xml1->setAttribute("type", "var");

                            if($readLine[2][0] == tokenVar){
                                $xml2 = $xml->createElement("arg2", htmlspecialchars($readLine[2][1] . "@" . $readLine[2][2]));
                                $xml2->setAttribute("type", "var");
                            }
                            else{
                                $xml2 = $xml->createElement("arg2", htmlspecialchars($readLine[2][2]));
                                $xml2->setAttribute("type", $readLine[2][1]);
                            }

                            if($readLine[3][0] == tokenVar){
                                $xml3 = $xml->createElement("arg3", htmlspecialchars($readLine[3][1] . "@" . $readLine[3][2]));
                                $xml3->setAttribute("type", "var");
                            }
                            else{
                                $xml3 = $xml->createElement("arg3", htmlspecialchars($readLine[3][2]));
                                $xml3->setAttribute("type", $readLine[3][1]);
                            }

                            $xmlInst->appendChild($xml1);
                            $xmlInst->appendChild($xml2);
                            $xmlInst->appendChild($xml3);
                        }
                        else{
                            print_Ds("Syntax: Fail - Expected: var, var/const, var/const");
                            exit(lexsynError);
                        }

                    }

                    # Label, Var/Const, Var/Const
                    else{
                        if($readLine[1][0] == tokenLabel && ($readLine[2][0] == tokenVar || $readLine[2][0] == tokenConst) && ($readLine[3][0] == tokenVar || $readLine[3][0] == tokenConst)){
                            print_Ds("Syntax: Success - label, var/const, var/const");
                            $xml1 = $xml->createElement("arg1", htmlspecialchars($readLine[1][1]));
                            $xml1->setAttribute("type", "label");
                            
                            if($readLine[2][0] == tokenVar){
                                $xml2 = $xml->createElement("arg2", htmlspecialchars($readLine[2][1] . "@" . $readLine[2][2]));
                                $xml2->setAttribute("type", "var");
                            }
                            else{
                                $xml2 = $xml->createElement("arg2", htmlspecialchars($readLine[2][2]));
                                $xml2->setAttribute("type", $readLine[2][1]);
                            }

                            if($readLine[3][0] == tokenVar){
                                $xml3 = $xml->createElement("arg3", htmlspecialchars($readLine[3][1] . "@" . $readLine[3][2]));
                                $xml3->setAttribute("type", "var");
                            }
                            else{
                                $xml3 = $xml->createElement("arg3", htmlspecialchars($readLine[3][2]));
                                $xml3->setAttribute("type", $readLine[3][1]);
                            }

                            $xmlInst->appendChild($xml1);
                            $xmlInst->appendChild($xml2);
                            $xmlInst->appendChild($xml3);

                            if($readLine[0][1] == 30 || $readLine[0][1] == 31){
                                array_push($jumpedBadLabels, $readLine[1][1]);

                                # Backjumps -> label already exists
                                if(in_array($readLine[1][1], $uniqueLabels) || in_array(($readLine[1][1] . "\n"), $uniqueLabels)){
                                    $backjumps++;
                                }        
                                # Possible forwardjump or badjump          
                                else{
                                    array_push($possiblyFwJump, $readLine[1][1]);
                                }
                            }


                        }
                        else{
                            print_Ds("Syntax: Fail - Expected: label, var/const, var/const");
                            exit(lexsynError);
                        }

                    }
                }
#===============================================================
                        # Error
#===============================================================
                else{

                    print_Ds("Syntax: Invalid instruction");
                    exit(wrongOpcode);
                }
                
            }
            $xmlMain->appendChild($xmlInst);
        }
    if($disableXML == false){
        echo($xml->saveXML());   
    }
    }




?>