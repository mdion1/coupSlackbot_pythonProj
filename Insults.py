import random

class InsultGenerator:
    def __init__(self):
        self._insultCatalog = open("trashtalk.txt","r").readlines()
        for line in self._insultCatalog:
            if len(line) == 0:
                self._insultCatalog.remove(line)
    def randomInsult(self):
        index = random.randint(0, len(self._insultCatalog) - 1)
        return self._insultCatalog[index]