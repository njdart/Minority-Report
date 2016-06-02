globalFlag = True

def ToggleGlobalFlag():
    global globalFlag
    globalFlag = not globalFlag

def GetGlobalFlag():
    global globalFlag
    return globalFlag