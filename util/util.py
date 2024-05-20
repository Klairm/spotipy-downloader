import re

def cleanString(string):
    return re.sub(r'[<>:"/\|?*]', '',string)

