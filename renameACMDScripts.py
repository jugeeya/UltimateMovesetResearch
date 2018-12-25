import idc
import idaapi
import idautils
import re

def decompile_func(ea):
    if not idaapi.init_hexrays_plugin():
        return False

    f = idaapi.get_func(ea)
    if f is None:
        return False

    cfunc = idaapi.decompile(f);
    if cfunc is None:
        # Failed to decompile
        return False

    lines = []
    sv = cfunc.get_pseudocode();
    for sline in sv:
        line = idaapi.tag_remove(sline.line);
        lines.append(line)
    return "\n".join(lines)

def getACMDName(scriptName):
    # game, effect, sound, expression
    if scriptName.startswith('me_'):
        return 'ga'+scriptName
    elif scriptName.startswith('fect_'):
        return 'ef'+scriptName
    elif scriptName.startswith('und_'):
        return 'so'+scriptName
    elif scriptName.startswith('pression_'):
        return 'ex'+scriptName
	
def animcmdHashTable(filetext):
    lines = filetext.split("\n")

    animation = ""
    functionName = ""
    hashTable = {}
    variableValues = {}
    inSetHashCall = False
    setHashParam = 0
	
    for line in lines:
        if "lib::L2CAgent::sv_set_function_hash" in line:
            if ");" in line:
                functionMatch = re.search('hash\(.*\, (\\w+)\,', line)
                if functionMatch:
                    functionName = functionMatch.group(1)
                    hashTable[functionName] = getACMDName(animation)
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
            print line, setHashParam
            if setHashParam == 1:
                setHashParam += 1
            elif setHashParam == 2:
                functionMatch = re.search('(\\w+)\,', line)
                if functionMatch:
                    functionName = functionMatch.group(1)
                setHashParam += 1
            elif setHashParam == 3:
                hashTable[functionName] = getACMDName(animation)
                inSetHashCall = False
                setHashParam = 0
                animation = ""
	    
    return hashTable
	
hashTable = animcmdHashTable(decompile_func(here()))
print "begin renaming"
for segea in Segments():
    for funcea in Functions(segea, SegEnd(segea)):
        functionName = GetFunctionName(funcea)
        if functionName in hashTable:
            if hashTable[functionName] != "":
				print hashTable[functionName]
				idc.MakeName(funcea, hashTable[functionName])
print "end renaming"