def function1(arg1: list):
    print("function1")
    print(arg1[0])

def function2(arg1: list):
    print("function2")
    print(arg1[1])


myDict = {}
myArgs = ["arg1", "arg2"]

class functionWrapper:
    def __init__(self, argListLengthMin: int, function):
        self._function = function
        self._argListLengthMin = argListLengthMin
    def execute(self, argList):
        if len(argList) >= self._argListLengthMin:
            self._function(argList)
        else:
            print("not enough args")

myDict["key1"] = functionWrapper(1, function1)
myDict["key2"] = functionWrapper(2, function2)
myDict["key3"] = functionWrapper(1, function1)

val1 = myDict["key1"]
val2 = myDict["key2"]
val3 = myDict["key3"]

val1.execute(myArgs)
val2.execute(myArgs)
val3.execute(myArgs)
val2.execute(myArgs[0:1])