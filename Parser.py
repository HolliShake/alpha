from Error import Error
from Node import Node
from Token import Token
from Lexer import Lexer


def expectT(cls, tokenType):
    return (cls.lookahead.tokenType == tokenType)

def expectS(cls, tokenValue):
    return (not expectT(cls, Token.STR)) and (cls.lookahead.tokenValue == tokenValue)

def consumeT(cls, tokenType):
    if  not expectT(cls, tokenType):
        # error
        return Error.RaiseError(
            cls.filePath,
            cls.fileCode,
            "unexpected token \"%s\"" % cls.lookeahead.tokenValue,
            cls.lineStart, 
            cls.colmStart,
            cls.previous.lineEnded,
            cls.previous.colmEnded
        )

    cls.previous  = cls.lookahead
    cls.lookahead = cls.lexer.nextToken()

def consumeS(cls, tokenValue):
    return (not expectT(cls, Token.STR)) and (cls.lookahead.tokenValue == tokenValue)


class Parser(object):

    def __init__(self, 
        gblState,
        filePath, 
        fileCode
    ):
        self.globalState = gblState
        self.filePath    = filePath
        self.fileCode    = fileCode
        self.lexer       = Lexer(self.__globalState, self.filePath, self.fileCode)

        self.lookahead = self.__lexer.nextToken()
        self.previous  = self.lookahead
    

    
    # ___________________________ BASE

    def __DatatypeOrVariableTypeBase(self, ttype, tnode):
        value = self.lookahead.tokenValue
        consumeT(self, ttype)
        return Node(
            tnode,
            value
        )


    def __DatatypeOrVariableSymbolBase(self, ttype, tnode):
        value = self.lookahead.tokenValue
        consumeT(self, ttype)

        return Node(
            tnode,
            value
        )
    

    def __BinaryExpressionBase(self, higherPrecedense, condition):
        look = self.lookahead
        node = higherPrecedense()
        
        if  not node:
            return node
    
        while condition:
            operator = self.lookahead
            
            right = higherPrecedense()
            if  not right:
                # error
                Error.RaiseError(
                    self.filePath,
                    self.fileCode,
                    "missing right-hand expression for operator \"%s\"" % operator.tokenValue,
                    look.lineStart, 
                    look.colmStart,
                    self.previous.lineEnded,
                    self.previous.colmEnded
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
        if  expectS(self, "true") or expectS(self, "false"):
           return self.__DatatypeOrVariableSymbolBase(
               Token.IDN, 
               Node.BOOLEAN
            )
    
        elif expectS(self, "null"):
            return self.__DatatypeOrVariableTypeBase(
                Token.IDN, 
                Node.NULL
            )
        
        elif expectT(self, Token.INT):
            return self.__DatatypeOrVariableTypeBase(
                Token.INT, 
                Node.INTEGER
            )
        
        elif expectT(self, Token.DBL):
            return self.__DatatypeOrVariableTypeBase(
                Token.DBL, 
                Node.DOUBLE
            )

        elif expectT(self, Token.CHR):
            return self.__DatatypeOrVariableTypeBase(
                Token.CHR, 
                Node.CHARACTER
            )
        
        elif expectT(self, Token.STR):
            return self.__DatatypeOrVariableTypeBase(
                Token.STR, 
                Node.STRING
            )

        elif expectT(self, Token.IDN):
            return self.__DatatypeOrVariableTypeBase(
                Token.IDN, 
                Node.IDENTIFIER
            )
        
        elif expectT(self, Token.LPAREN):
            consumeT(self, Token.LPAREN)
            node = self.__NonNullableExpression()
            consumeT(self, Token.RPAREN)
            return node
        
        else:
            return None


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
                self.filePath,
                self.fileCode,
                "expression is expected, got \"%s\"" % self.lookahead.tokenValue,
                self.lookahead.lineStart, 
                self.lookahead.colmStart,
                self.lookahead.lineEnded,
                self.lookahead.colmEnded
            )

    def parseInput(self):
        ...

