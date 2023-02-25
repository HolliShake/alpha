from Error import Error
from Node import Node
from Lexer import Lexer


def expectT(cls, tokenType):
    return (cls.__lookahead.tokenType == tokenType)


class Parser(object):

    def __init__(self, 
        gblState,
        filePath, 
        fileCode
    ):
        self.__globalState = gblState
        self.__filePath    = filePath
        self.__fileCode    = fileCode
        self.__lexer = Lexer(self.__globalState, self.__filePath, self.__fileCode)


        self.__lookahead = self.__lexer.nextToken()
        self.__previous  = self.__lookahead
    

    def __GetPrimary(self):
        ...
    

    def __BinaryExpressionBase(self, lhsCallback, condition, rhsCallback):
        look = self.__lookahead

        node = lhsCallback()
        if  not node:
            return node
    
        while condition:
            operator = self.__lookahead
            
            right = rhsCallback()
            if  not right:
                # error
                Error.RaiseError(
                    self.__filePath,
                    self.__fileCode,
                    "inclomplete other literal \"%s\"" % look.tokenValue,
                    look.lineStart, 
                    look.colmStart,
                    self.__previous.lineEnded,
                    self.__previous.colmEnded
                )

            node = Node(
                Node.BINARYEXPRESSION,
                node, 
                operator.tokenValue,
                right
            )
        
        return node

    def parseInput(self):
        ...

