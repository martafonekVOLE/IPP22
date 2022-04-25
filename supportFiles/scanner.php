<?php
    # function checkIfInstruction - responsible for looping through
    # the "instructions" array and finding one
    function checkIfInstruction($testInst){
        global $instructions;

        foreach($instructions as $key => $inst){
            if(preg_match("/^" . $inst . "$/i", $testInst)){      #loop over array
                return($key);                              #if you found instruction, return key
            }
            else{
                #else return -1
            }
        }
        return -1;
    }

    # function scan - responsible for lexical analysis
    function scan(){
        $result = array();
        global $amountOfComments;
        global $amountOfLabels;
        global $amountOfJumps;

        $isName = 0;
        global $acceptLabel;
        global $instructions;


        while(true){

            global $IN;
            $readLine = fgets($IN);

            # is EOF
            if($readLine == false){ 
                print_Dl("Lexem : Identified as EOF");
                array_push($result, array(tokenEOF));
                return $result;
            }
            else if($readLine == "\n"){  #(preg_match("/^\s*\n$/", $w));
                continue;
            }
            # is comment
            else if(preg_match("/^\s*#/", $readLine)){  
                print_Dl("Lexem : Identified as comment\n\nLexem : Requesting next token");
                $amountOfComments++;
                continue;   
            }
            else{
                if(preg_match("/^\s*\n$/", $readLine)){
                    continue;
                }
            }

            # separating words by delimiter
            if(preg_match("/#/", $readLine)){
                $amountOfComments++;
            }

            $comments = explode("#", $readLine);
            $word = explode(" ", $comments[0]);

            foreach($word as $removeKkey => $removeW){
                if($removeW == "" || $removeW == " "){
                    unset($word[$removeKkey]);
                }
            }

            # scanner implementation
            foreach($word as $w){

                # is Variable or Constant - contains @
                if(preg_match("/@/", $w)){  

                    # is Constant - beggins with int, bool or string
                    if(preg_match("/^(int|bool|string|nil)/",$w)){
                        # context
                        $isName--;

                        #is correct
                        if(preg_match("/^int@[+-]?[0-9]+/"/*$*/, $w)||
                        preg_match("/^bool@(true|false)/", $w)||
                        preg_match("/^string@/", $w)||
                        preg_match("/^nil@nil$/", $w)){ 
                            if(preg_match("/^string@/", $w) && str_contains($w, '\\')){
                                print_Dl("Lexem : Found string with backslash");

                                $checkBackslash = array();
                                $checkBackslash = explode("\\", $w);
                                foreach($checkBackslash as $isCorrect){
                                    if(strlen($isCorrect) == 0){
                                        print_Dl("Lexem : Fail - Invalid escape sequence");
                                        exit(lexsynError);
                                    }
                                    else if(is_numeric($isCorrect[0])){
                                        if(!is_numeric($isCorrect[1]) || !is_numeric($isCorrect[2])){
                                            print_Dl("Lexem : Fail - Invalid escape sequence");
                                            exit(lexsynError);
                                        }
                                    }
                                }
                            }
                            print_Dl("Lexem : Identified as Constant");
                            array_push($result, array_merge(array(tokenConst), explode("@", $w)));
                        }
                        # incorrect
                        else{ 
                            print_Dl("Lexem : Fail - Constant");
                            exit(lexsynError);
                        }
                    }

                    # is Variable
                    else{
                        # context
                        $isName--;

                        # is correct
                        if(preg_match("/^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*/", $w)){ 
                            array_push($result, array_merge(array(tokenVar), explode("@", $w)));
                            print_Dl("Lexem : Identified as Variable");
                        }
                        # incorrect
                        else{
                            print_Dl("Lexem : Fail - Variable");
                            exit(lexsynError);
                        }
                    }
                }

                # is Opcode, Label or header
                else{

                    # is header - contains ippcode22
                    if(preg_match("/^\.ippcode22$/i", $w)){
                        # context 
                        $isName--;

                        array_push($result, array(tokenHeader));
                        print_Dl("Lexem : Identified as Header");
                        $acceptLabel = false;
                    }

                    # is type
                    else if(preg_match("/^(string|bool|int)$/", $w)){
                        # context
                        $isName--;

                        array_push($result, array(tokenType, $w));
                        print_Dl("Lexem : Identified as Type");
                    }

                    # is opcode or label
                    else{                         
                        # is opcode - contains one of accepted instructions (MOVE, POPS,...)
                        if(checkIfInstruction($w) != -1 && ($isName <= 0)){
                            # context
                            $isName--;

                            array_push($result, array(tokenOpcode, checkIfInstruction($w)));
                            print_Dl("Lexem : Identified as Opcode");                                 
                            if(preg_match("/label/i", $w)){
                                $amountOfLabels++;
                                # context
                                $isName = 1;
                                $acceptLabel = true;
                            }
                            if(preg_match("/jump/i", $w) || preg_match("/jumpifeq/i", $w) || preg_match("/jumpifneq/i", $w) || preg_match("/call/i", $w) || preg_match("/return/i", $w) || preg_match("/return\n/i", $w)){  #lib_poc_mez
                                
                                # context
                                if(preg_match("/jump/i", $w) || preg_match("/jumpifeq/i", $w) || preg_match("/jumpifneq/i", $w) || preg_match("/call/i", $w)){
                                    $isName = 1;
                                    $acceptLabel = true;
                                }

                                $amountOfJumps++;
                            }

                        }

                        # is correct label
                        else{
                            # context
                            $isName--;

                            if(preg_match("/^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*/", $w) && $acceptLabel == true){
                                array_push($result, array(tokenLabel, $w));
                                print_Dl("Lexem : Identified as Label");
                                $acceptLabel = false;
                            }
                            # is empty line
                            else if(preg_match("/^\s*\n$/", $w)){
                                continue;
                            }
                            # is incorrect
                            else{
                                if(preg_match("/^\.ippcode22/i", $w) || preg_match("/ippcode22/i", $w)){
                                    print_Dl("Lexem : Fail - invalid/missing header");
                                    exit(missingHeader);
                                }
                                foreach($instructions as $testInst){
                                    if(strpos($w, $testInst) !== FALSE){
                                        print_Dl("Lexem : Fail - No space between opcode and operand");
                                        exit(wrongOpcode);
                                    }
                                }
                                print_Dl("Lexem : Fail - Label/Opcode");
                                exit(lexsynError);
                            }
                        }
                    }

                }
            }
            return $result;
        }
        
    }
    # Useful links: 
        # https://regex101.com/
        # https://lzone.de/examples/PHP%20preg_match
?>