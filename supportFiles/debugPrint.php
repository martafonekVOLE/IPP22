<?php
    # Debug print for syntax.php
    function print_Ds($toPrint){
        global $allowSyntaxOutput;

        if($allowSyntaxOutput == true){
            fwrite(STDERR, $toPrint . "\n");
        }
    }

    # Debug print for scanner.php
    function print_Dl($toPrint){
        global $allowLexemOutput;

        if($allowLexemOutput == true){
            fwrite(STDERR, $toPrint . "\n");
        }
    }

    function print_help(){
        echo("---------------------\nPARSE.PHP\nAuthor: Martin Pech (xpechm00)\n---------------------\n");
        echo("This script is used for interpretation of the unstructured imperative langueage IPPcode22\n---------------------\nUsage:");
        echo("\n\t--help -> Prints this prompt\n");
        echo("\n\t===============\n\tSTATP - writes information about source code into file\n\t===============");
        echo("\n\t--stats=file, where file is a name of file -> file to save stats into\n");
        echo("\n\tThis argument can be followed by:\n");
        echo("\t--loc -> Prints amount of instruction\n");
        echo("\t--comments -> Prints amount of comments\n");
        echo("\t--labels -> Prints amount of unique labels\n");
        echo("\t--jumps -> Prints amount of jumps (jumps, calls and returns)\n");
        echo("\t--fwjumps -> Prints amount of forward jumps\n");
        echo("\t--backjumps -> Prints amount of backward jumps\n");
        echo("\t--badjumps -> Prints amount of bad jumps (jumps on undefined labels)\n");
        echo("\t===============\nIf --stats is not followed by any other argument, empty file will be created.\nIf there are only other argument, program will end with error code 10\n\n");
    }
?>