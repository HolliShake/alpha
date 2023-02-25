

class Node(object):

    BINARYEXPRESSION = 0

    def __init__(self, nodeType, *args):
        self.__parameter = args
        self.nodeType    = nodeType
    

    def get(self, index):
        return self.__parameter[index]

