def evalMacro(header, macro):
    import subprocess

    command = "g++ -I$SHOAL_PATH/share/include \
        -I$SHOAL_VIVADO_HLS -I$SHOAL_PATH/GASCore/include \
        $SHOAL_PATH/share/src/eval_macro.cpp -w \
        -include $SHOAL_PATH/" + header + " -DMACRO_VALUE=" + \
        macro + " -o $SHOAL_PATH/share/build/bin/eval_macro"

    subprocess.call(command, shell=True)
    return subprocess.check_output("$SHOAL_PATH/share/build/bin/eval_macro", shell=True)

if __name__ == "__main__":

    for arg in sys.argv:
        if arg == "-h" or arg == "--help":
            print("Usage: python share.py [function] [args...]")
            print("Functions: ")
            print("   evalMacro header macro, returns int")
            exit(1)

    if (len(sys.argv) > 1):
        if sys.argv[1] == "evalMacro" and len(sys.argv) == 4:
            print(evalMacro(sys.argv[2], sys.argv[3]))
        else:
            print("Unknown flags. Use -h or --help")
    else:
        print("Needs flags. Use -h or --help")