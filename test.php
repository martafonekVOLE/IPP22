<?php
# Author: Martin Pech (xpechm00)
################################
# Main
################################
date_default_timezone_set('Europe/Berlin');

# Tokens
$tokenHELP = false;
$tokenDIRECTORY = false;
$tokenRECURSIVE = false;
$tokenPARSE_SCRIPT = false;
$tokenINT_SCRIPT = false;
$tokenPARSE_ONLY = false;
$tokenINT_ONLY = false;
$tokenJEXAMPATH = false;
$tokenCLEAN = true;

# paths
$testDirectoryPath = "";
$parsePHP = "";
$interpretPY = "";
$jexampath = "";

# counters
$allTests = 0;
$okTests = 0;
$nokTests = 0;
$i = 0;

# arguments processing
foreach ($argv as $arg){
    if(preg_match("/^test.php$/", $arg)){
        continue;
    }
    elseif(preg_match("/^--help/", $arg)){
        if($argc > 2){
            exit(10);
        }
        else{
            helpPrint(); 
        }
    }
    elseif(preg_match("/^--directory=/", $arg)){
        $tokenDIRECTORY = true;
        $path = explode("=", $arg);
        $testDirectoryPath = $path[1];
    }
    elseif(preg_match("/^--recursive$/", $arg)){
        $tokenRECURSIVE = true;
    }
    elseif(preg_match("/^--parse-script=/", $arg)){
        $path = explode("=", $arg);
        $parsePHP = $path[1];
        $tokenPARSE_SCRIPT = true;
    }
    elseif(preg_match("/^--int-script=/", $arg)){
        $path = explode("=", $arg);
        $interpretPY = $path[1];
        $tokenINT_SCRIPT = true;
    }
    elseif(preg_match("/^--parse-only$/", $arg)){
        $tokenPARSE_ONLY = true;
    }
    elseif(preg_match("/^--int-only$/", $arg)){
        $tokenINT_ONLY = true;
    }
    elseif(preg_match("/^--jexampath=/", $arg)){
        $path = explode("=", $arg);
        $jexampath = $path[1];
        $tokenJEXAMPATH = true;
    }
    elseif(preg_match("/^--noclean$/", $arg)){
        $tokenCLEAN = false;
    }
    else{
        debug("Testing script: Invalid argument: " . $arg);
        exit(10); 
    }
}
debug("Testing script: All arguments are correct.");


# banned combinations checking
if($tokenPARSE_ONLY == true && ($tokenINT_ONLY == true || $tokenINT_SCRIPT == true)){
    exit(10);
}
if($tokenINT_ONLY == true && ($tokenPARSE_ONLY == true || $tokenPARSE_SCRIPT == true)){
    exit(10);
}

# used while testing parse & interpret simultaneously
if($tokenINT_SCRIPT == true && $tokenPARSE_SCRIPT == true){
    $tokenPARSE_ONLY = true;
    $tokenINT_ONLY = true;
}

# Checking paths/implicit paths
if(empty($testDirectoryPath)){
    $testDirectoryPath = getcwd();
}
if(empty($parsePHP) && ($tokenPARSE_ONLY == true)){
    $parsePHP = getcwd() . "/parse.php";
}
if(empty($interpretPY) && ($tokenINT_ONLY == true)){
    $interpretPY = getcwd() ."/interpret.py";
}
if(empty($jexampath)){
    $jexampath = "/pub/courses/ipp/jexamxml/.jexamxml";
}
if(!file_exists($testDirectoryPath) || !file_exists($parsePHP) && $tokenPARSE_ONLY == true || !file_exists($interpretPY) && $tokenINT_ONLY == true || !file_exists($jexampath) && $tokenJEXAMPATH == true){
    debug("Testing script: Selected file does not exist");
    exit(41);
}

# testing and generating results
generateHTMLhead();
generateHTMLbody();
generateCSSstyle();
$newTest = new Testing;
$newTest->start($testDirectoryPath);
if($tokenCLEAN == true){
    exec("rm -f temp_diff temp_output temp_output_php temp_xml temp_diff.log temp_output.log temp_xml.log temp_diff.log");
}
displaySuccessRate();
generateHTMLend();

################################
# Functions
################################
# display help prompt
function helpPrint(){
    echo("---------------------\nTEST.PHP\nAuthor: Martin Pech (xpechm00)\n---------------------\n");
    echo("This script is used testing INTERPRET.PY & PARSE.PHP for imperative langueage IPPcode22\n---------------------\nUsage:");
    echo("\n\t--help -> Prints this prompt\n");
    echo("\n\t--directory=path -> Searches directory for tests");
    echo("\n\t--recursive -> Searches --directory subdirectories for tests");
    echo("\n\t--parse-script=file -> PHP script (implicit value: parse.php)");
    echo("\n\t--int-script=file -> PY script (implicit value: interpret.py)");
    echo("\n\t--parse-only -> Only PHP script will be tested, cannot be combined with --int-script, --int-only");
    echo("\n\t--int-only -> Only PY script will be tested, cannot be combined with --parse-script, --parse-only");
    echo("\n\t--jexampath=path -> Path to directory with jexamxml.jar which is used to compare XML files. (implicit value: /pub/courses/ipp/jexamxml *Merlin)");
    echo("\n\t--noclean Does not clean temp files, that are created while testing");
    exit(0);
}
# generate html head
function generateHTMLhead(){
    echo "<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"UTF-8\">\n<title>IPP testovací script</title>\n</head>\n";
}
# generate css styling
function generateCSSstyle(){
    # nicer font, cannot be used
    // echo "<style>\n@import url('https://fonts.googleapis.com/css?family=Poppins:200,300,400,500,600,700,800,900&display=swap');\n
    // *{font-family: 'Poppins', sans-serif;}\nbody{\n;background-color: #27dbba;}\n
    // h1{\nfont-size: 42px; font-weight: 600;\ntext-align: center;\npadding: 5px;\nmargin-bottom: 5%;\n}\n";

    # comment block bellow if you want to use Poppins
    echo "<style>\n 
    *\nbody{\n;background-color: #27dbba;}\n
    h1{\nfont-size: 42px; font-weight: 600;\ntext-align: center;\npadding: 5px;\nmargin-bottom: 5%;\n}\n";

    echo "h1 span{font-weight: 600; color: #444444}h3{text-align: center;margin-bottom: 1.5%;\n
    line-height: 0%;\n}\np{text-align:center;}table, td, tr{margin-left: auto; margin-right: auto;
    border-collapse: collapse;\nwidth: 800px;\n}\ntr{border-bottom: 1px solid;}";

    echo "td, tr{\ntext-align: left;\n}\ntd{padding-top:10px; padding-bottom:10px;}</style>\n";
}
#generate html body
function generateHTMLbody(){
    echo " <body>\n";
    echo "<h1>IPP - Test.php pro jazyk <span>IPPcode22</span></h1>\n";

    $real_input = $GLOBALS['argv'];
    echo "<h3>Test byl spuštěn s následujícími parametry:</h3><p>";
    if(count($real_input) == 1){
        echo " ";
    }
    for($i = 1; $i < count($real_input); $i++){
        if($real_input[$i] == true){
            echo " $real_input[$i]";
        }
    }
    echo "</p>";
    echo "<p>Test proveden dne  " . date("d.m.Y") . " v " . date("H:i") . ".</p><br>";
    echo "<h3>Byly provedeny následující testy:</h3>\n";
    echo "<table>\n<tr>\n<th>Číslo:</th>\n<th>Cesta</th>\n<th>TestCase:</th>\n<th>Stav:</th>\n</tr>\n";
}
# generate html footer
function generateHTMLend(){
    // if($percentage != 100){
    //     echo "<p>Podrobnější informace o výsledcích testů (a důvodech jejich pádů) jsou k nalezení v terminálu, ze kterého byl tento skript spuštěn.</p>
    //     <p>Poznámka: Pokud je nevidíte, přepněte prosím v <b>interpret.py</b> následující spínač <i>switches.allowDebugPrint</i> na hodnotu <i>true</i>.</p>";
    // }
    echo "</body>\n";
    echo "</html>\n";
}
# calculates percentage success of tests
function displaySuccessRate(){
    global $allTests, $okTests, $nokTests;
    $percentage = ($okTests / $allTests) * 100;
    $percentage = number_format((float)$percentage, 2, '.', '');

    echo "<p>Provedeno celkem testů: $allTests</p>";
    echo "<p>z toho úspěšných: $okTests</p>";

    if($percentage < 0.3){
        echo "<p style='color: red; font-size: 40px;'>$percentage%</p>";
    }
    elseif($percentage > 0.8){
        echo "<p style='color: green; font-size: 40px;'>$percentage%</p>";
    }
    else{
        echo "<p style='color: yellow; font-size: 40px;'>$percentage%</p>";
    }
}
# prints message to stderr
function debug($message){
    fwrite(STDERR, $message . "\n");
}
################################
# Object
################################
class Testing{
        # Method start
        #   Declares weather given path is directory or file
        #   If it is directory, it calls itself recursivelly
        #   If it is file with correct format, it checks for
        #   other neccessary files (.in, .out, .rc)
        #   If all the files are correct, it calls method test
        function start($testDirectoryPath){
            global $tokenCLEAN, $tokenDIRECTORY, $tokenHELP, $tokenINT_ONLY, $tokenINT_SCRIPT, $tokenJEXAMPATH, $tokenPARSE_ONLY, $tokenPARSE_SCRIPT, $tokenRECURSIVE;
            global $parsePHP, $interpretPY;

            $directory = $testDirectoryPath;
            if($tokenDIRECTORY == true){
                $directoryCheck = opendir($testDirectoryPath);
            }

            # ignoring . and .. files 
            while($actual = readdir($directoryCheck)){
                if($actual == "." || $actual == ".."){
                    continue;
                }
                #
                if(is_file($directory . "/" . $actual)){
                    if(pathinfo(($directory . "/" . $actual), PATHINFO_EXTENSION) == "src"){
                        if(!file_exists($directory . "/" . pathinfo(($actual),PATHINFO_FILENAME) . ".in")){
                            $editFile = fopen($directory . "/" . $actual . ".in", "w");
                            fclose($editFile);
                        }
                        if(!file_exists($directory . "/" . pathinfo(($actual),PATHINFO_FILENAME) . ".out")){
                            $editFile = fopen($directory . "/" . $actual . ".out", "w");
                            fclose($editFile);
                        }
                        if(!file_exists($directory . "/" . pathinfo(($actual),PATHINFO_FILENAME) . ".rc")){
                            $editFile = fopen($directory . "/" . $actual . ".rc", "w");
                            fwrite($editFile, 0);
                            fclose($editFile);
                        }
                        self::test($directory, $actual, $parsePHP, $interpretPY);
                    }
                }
                # Recursive call of this method
                elseif(is_dir($directory . "/" . $actual) && $tokenRECURSIVE == true){
                    self::start(($directory . "/" . $actual));
                }
                else{
                    debug("Testing script: File is not file or directory");
                    exit(1);
                }
            }
    }
    # Method test
    #   gets expected output code. If exit codes do match
    #   test outputs are compared
    #   After test has been run it call method test_result
    function test($directory, $actual, $parsePHP, $interpretPY){
        global $tokenCLEAN, $tokenDIRECTORY, $tokenHELP, $tokenINT_ONLY, $tokenINT_SCRIPT, $tokenJEXAMPATH, $tokenPARSE_ONLY, $tokenPARSE_SCRIPT, $tokenRECURSIVE;
        #global $parsePHP, $interpretPY;
        global $allTests, $okTests, $nokTests;
        $allTests++;


        $f = fopen($directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)) . ".rc", "r");
        $rc = fgets($f);
        fclose($f);

        # Testing Interpret only -> diff 
        if($tokenINT_ONLY == true && $tokenPARSE_ONLY == false){
            exec("python3.8 " . $interpretPY . " --source=" . $directory ."/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)) . ".src" . " --input=" . $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)) . ".in > temp_output", $exit_array, $exit_code); 
            if($exit_code == $rc){
                if($exit_code == 0){
                    exec("diff temp_output " . $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)) . ".out > temp_diff");
                    if(filesize("temp_diff") != 0){
                        $nokTests ++;
                        self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), false);
                    }
                    else{
                        $okTests ++;
                        self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), true);
                    }

                }
                else{
                    $okTests ++;
                    self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), true);
                }
            }
            else{
                $nokTests ++;
                self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), false);
            }
        }

        # Testing Parse only -> jexamxml
        elseif($tokenPARSE_ONLY == true && $tokenINT_ONLY == false){
            exec("php8.1 " . $parsePHP . "<" . $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)). ".src > temp_output", $exit_array, $exit_code);
            if($exit_code == $rc){
                if($exit_code == 0){
                    global $jexampath;
                    exec('java -jar ' . $jexampath . '/jexamxml.jar' . ' temp_output ' . $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)) . ".out > temp_xml");
                    $same = false;
                    $f = fopen("temp_xml", "r");

                    while(fgets($f) != false){    
                        if(fgets($f) == "Two files are identical" || fgets($f) == "Two files are identical\n"){
                            $same = true;
                        }
                    }

                    if($same == true){
                        $okTests ++;
                        self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), true);    
                    }
                    else{
                        $nokTests ++;
                        self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), false);
                    }
                }  
                else{
                    $okTests ++;
                    self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), true);
                }
            }
            else{
                $nokTests++;
                self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), false);
            }
        }

        # Testing both Interpret and Parse
        else{
            exec("php8.1 " . $parsePHP . "<" . $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)). ".src > temp_output_php", $exit_array, $exit_code);
            exec("python3.8 " . $interpretPY . " --source=temp_output_php" . " --input=" . $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)) . ".in > temp_output", $exit_array, $exit_code); 
            if($exit_code == $rc){

                if($exit_code == 0){
                    exec("diff temp_output " . $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)) . ".out > temp_diff");
                    if(filesize("temp_diff") == 0){
                        $okTests++;
                        self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), true);
                    }
                    else{
                        $nokTests++;
                        self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), false);
                    }
                }
                else{
                    $okTests++;
                    self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), true);
                }
            }
            else{
                $nokTests++;
                self::test_result($allTests, $directory . "/" . (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), (pathinfo(($directory . "/" . $actual), PATHINFO_FILENAME)), false);
            }
        }
    }
    # Method test_result
    #   Calculates pecentage of successfull tests
    #   based on values sent by method test
    function test_result($testNumber, $path, $testName, $result){
        echo "            <tr>\n";
        echo "                <td>$testNumber</td>\n";
        echo "                <td>$path</td>\n";
        echo "                <td>$testName</td>\n";
        if($result == true){ 
            echo "                <td style=\"color:green\">Úspěch</td>\n";
        }
        else{          
            echo "                <td style=\"color:red\">Neúspěch</td>\n";
        }
        echo "            </tr>\n";
    }
}
?>