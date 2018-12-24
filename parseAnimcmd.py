import os, sys, re

def animcmdHashTable(filename):
    lines = []
    with open(filename) as f:
        lines = f.readlines()

    animation = ""
    functionName = ""
    hashTable = {}
    variableValues = {}
    inSetHashCall = False
    setHashParam = 0
    
    for line in lines:
        if "lib::L2CAgent::sv_set_function_hash" in line:
            if ");" in line:
                functionMatch = re.search('\ (sub\_.*)\,', line)
                if functionMatch:
                    functionName = functionMatch.group(1)
                    hashTable[animation] = functionName
                    print(animation, hashTable[animation])
                    animation = ""
            else:
                inSetHashCall = True
                setHashParam = 1
                continue

        charMatch = re.search('(v\\d*) = phx::detail::CRC32Table::table\_.*(v\\d*)\ \^\ (0x..)', line)
        charMatchCall = re.search('phx::detail::CRC32Table::table\_.*(v\\d*)\ \^\ (0x..)', line)
        setVarMatch = re.search('(v\\d*).*(v\\d*).*;', line)
        if charMatch:
            varSet = charMatch.group(1)
            varGet = charMatch.group(2)
            
            charHex = int(charMatch.group(3), 16)
            if charHex <= 122:
                if varGet in variableValues:
                    variableValues[varSet] = variableValues[varGet] + chr(charHex)
                    animation = variableValues[varSet]
                else:
                    variableValues[varSet] = chr(charHex)
                    animation = variableValues[varSet]
        elif charMatchCall:
            varGet = charMatchCall.group(1)
            charHex = int(charMatchCall.group(2), 16)
            if charHex <= 122:
                animation = variableValues[varGet] + chr(charHex)
        elif setVarMatch:
            varSet = setVarMatch.group(1)
            varGet = setVarMatch.group(2)
            try:
                variableValues[varSet] = variableValues[varGet]
            except:
                continue
            animation = variableValues[varSet]

        if inSetHashCall:
            if setHashParam == 2:
                functionMatch = re.search('\ (.*)\,', line)
                if functionMatch:
                    functionName = functionMatch.group(1)
            elif setHashParam == 3:
                hashTable[animation] = functionName
                inSetHashCall = False
                setHashParam = 0
                print(animation, hashTable[animation])
                animation = ""
                continue
            setHashParam += 1


def main():
    animcmdHashTable(sys.argv[1])

main()
