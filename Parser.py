from Error import Error
from Node import Node
from Token import Token
from Lexer import Lexer


def expectT(cls, tokenType):
    return (cls.__lookahead.tokenType == tokenType)

def expectS(cls, tokenValue):
    return (not expectT(cls, Token.STR)) and (cls.__lookahead.tokenValue == tokenValue)


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
    

    
    # ___________________________ BASE

    def __BinaryExpressionBase(self, higherPrecedense, condition):
        look = self.__lookahead
        node = higherPrecedense()
        
        if  not node:
            return node
    
        while condition:
            operator = self.__lookahead
            
            right = higherPrecedense()
            if  not right:
                # error
                Error.RaiseError(
                    self.__filePath,
                    self.__fileCode,
                    "missing right-hand expression for operator \"%s\"" % operator.tokenValue,
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

    # ___________________________ PARSING
    
    def __GetPrimary(self):
        ...


    def __ExponentialExpression(self):
        return self.__BinaryExpressionBase(
            self.__GetPrimary,
            (expectS(self, "**"))
        )


    def __AddetiveExpression(self):
        return self.__BinaryExpressionBase(
            self.__ExponentialExpression,
            (expectS(self, "+") or 
             expectS(self, "-"))
        )


    def __MultiplicativeExpression(self):
        return self.__BinaryExpressionBase(
            self.__AddetiveExpression,
            (expectS(self, "*") or 
             expectS(self, "/") or 
             expectS(self, "%"))
        )


    def __BitwiseShiftExpression(self):
        return self.__BinaryExpressionBase(
            self.__MultiplicativeExpression,
            (expectS(self, ">>") or 
             expectS(self, "<<"))
        )


    def __RelationalExpression(self):
        return self.__BinaryExpressionBase(
            self.__BitwiseShiftExpression,
            (expectS(self, "<" ) or 
             expectS(self, "<=") or 
             expectS(self, ">" ) or 
             expectS(self, ">="))
        )


    def __EqualityExpression(self):
        return self.__BinaryExpressionBase(
            self.__RelationalExpression,
            (expectS(self, "==") or 
             expectS(self, "!="))
        )


    def __BitwiseLogicExpression(self):
        return self.__BinaryExpressionBase(
            self.__EqualityExpression,
            (expectS(self, "&") or 
             expectS(self, "|") or 
             expectS(self, "^"))
        )


    def __LogicalExpression(self):
        return self.__BinaryExpressionBase(
            self.__BitwiseLogicExpression,
            (expectS("&&") or 
             expectS("||"))
        )


    def __NullableExpression(self):
        return self.__LogicalExpression()


    def __NonNullableExpression(self):
        node = self.__NullableExpression()
        if  not node:
            # error
            Error.RaiseError(
                self.__filePath,
                self.__fileCode,
                "expression is expected, got \"%s\"" % self.__lookahead.tokenValue,
                self.__lookahead.lineStart, 
                self.__lookahead.colmStart,
                self.__lookahead.lineEnded,
                self.__lookahead.colmEnded
            )

    def parseInput(self):
        ...

