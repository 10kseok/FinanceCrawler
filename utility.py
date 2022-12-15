import re


def only_num(content) -> str:
    num = re.sub(r'[^0-9]', '', content)
    return num

class S():
    def __init__(self):
        self._name = "hey"

class T(S):
    def __init__(self):
        super().__init__()

    def printname(self):
        print(self._name)

if __name__ == "__main__":
    # print(only_num('24 sad  ,386,473'))
    t = T()
    t.printname()
