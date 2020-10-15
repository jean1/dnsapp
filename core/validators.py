import re

# Namespace name
namespacenameformat='^[-0-9a-z.]+$'
def CheckNamespacenameFormat(name):
    return (re.match(namespacenameformat, name) != None)

# Zone name
zonenameformat='^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.){1,126}[A-Za-z]{2,63}$'
def CheckZonenameFormat(name):
    return (re.match(zonenameformat, name) != None)

# Rr name
start = '(\*\.|_)?'               # can start with "*." or "_"
middle='(?!-)[A-Za-z0-9.-]{1,63}' # name can contain alphanum. char, dot or dash
end='(?<![-.])'                   # does not end with dash or dot
rrname1=start+middle+end
rrnameformat='^(@|'+rrname1+')$'
def CheckRrNameFormat(name):
    return (re.match(rrnameformat, name) != None)
