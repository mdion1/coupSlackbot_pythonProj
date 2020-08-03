class functionWrapper:
    def __init__(self, argListLengthMin: int, function, errMsgToDisplay = ""):
        self._function = function
        self._argListLengthMin = argListLengthMin
        self._errMsg = errMsgToDisplay
    def execute(self, argList: list, userId: str):
        if len(argList) >= self._argListLengthMin:
            self._function(argList, userId)
            return ""
        else:
            return self._errMsg