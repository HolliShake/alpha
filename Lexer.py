from Token import Token
from Error import Error


class Checker:

    @staticmethod
    def IsIgnoreable(char):
        c = ord(char)
        return (
            (c ==  0) or
            (c ==  8) or 
            (c ==  9) or 
            (c == 10) or 
            (c == 13) or 
            (c == 32)
        )

    @staticmethod
    def IsIdentifier(char):
        if  Checker.IsAsciiIdentifierStart(char):
            return True
        
        return Checker.IsUnicodeIdentifierStart(char)

    @staticmethod
    def IsAsciiIdentifierStart(char):
        c = ord(char)
        return (
            (c >= 65 and c <=  90) or 
            (c >= 97 and c <= 122) or 
            (c == 95)
        )
    
    @staticmethod
    def IsUnicodeIdentifierStart(char):
        return char.isidentifier()


    @staticmethod
    def IsNumber(char):
        c = ord(char)
        return (c >= 48 and c <= 57)
    

    @staticmethod
    def IsHex(char):
        c = ord(char)
        return (
            ((c >= 97) and (c <= 102)) or 
            ((c >= 65) and (c <=  70)) or 
            Checker.IsNumber(char)
        )
    

    @staticmethod
    def IsOct(char):
        c = ord(char)
        return ((c >= 48) and (c <= 55))
    

    @staticmethod
    def IsBin(char):
        c = ord(char)
        return ((c == 48) or (c == 49))


    @staticmethod
    def IsCharacter(char):
        return (ord(char) == 39)
    

    @staticmethod
    def IsString(char):
        return (ord(char) == 34)



class Lexer(object):


    def __init__(self, 
        gblState,
        filePath,
        fileCode
    ):
        self.__globalState = gblState
        self.__filePath    = filePath
        self.__fileCode    = fileCode


        self.__index = 0
        self.__ahead = (
            "\0" if len(self.__fileCode) <= 0 
            else self.__fileCode[0]
        )


        self.__colm = 1
        self.__line = 1

        self.__colmBefore = 1
        self.__lineBefore = 1


    def __Forward(self):
        if  self.__ahead == "\n":
            self.__colmBefore = self.__colm
            self.__lineBefore = self.__line

            self.__line += 1
            self.__colm  = 1
        
        else:
            self.__colmBefore = self.__colm
            self.__lineBefore = self.__line

            self.__colm += 1
        
        self.__index += 1
        self.__ahead = (
            "\0" if self.__IsEof()
            else self.__fileCode[self.__index]
        )
    

    def __MoveForward(self):
        old = self.__ahead
        self.__Forward()
        return old

    
    def __MakeIdentifier(self):
        line, colm = self.__line, self.__colm
        idenifier  = self.__IdentifierStart()
        idenifier += self.__IdentifierParts()
        return Token(
            Token.IDN, 
            idenifier, 
            line, 
            colm, 
            self.__lineBefore, 
            self.__colmBefore
        )
    

    def __IdentifierStart(self):
        part = ""
        while not self.__IsEof() and \
            Checker.IsIdentifier(self.__ahead):
            part += self.__MoveForward()
        
        return part
    

    def __IdentifierParts(self):
        part = ""
        while not self.__IsEof() and \
            Checker.IsIdentifier(self.__ahead) or \
            Checker.IsNumber(self.__ahead):
            part += self.__MoveForward()
        
        return part
    

    def __MakeNumber(self):
        line, colm = self.__line, self.__colm
        number = self.__NumberPart()

        if  number == "0":
            if  self.__ahead in ("x", "X"):
                number += self.__MoveForward() + self.__HexPart()
            
            elif  self.__ahead in ("o", "O"):
                number += self.__MoveForward() + self.__OctPart()
            
            elif self.__ahead in ("b", "B"):
                number += self.__MoveForward() + self.__BinPart()

            if  len(number) == 2:
                # error
                Error.RaiseError(
                    self.__filePath,
                    self.__fileCode,
                    "inclomplete other literal \"%s\"" % number,
                    line, 
                    colm,
                    self.__lineBefore,
                    self.__colmBefore
                )

        # whole number or floating points
        ttype = Token.INT

        if  self.__ahead == ".":
            number += self.__MoveForward()

            if  not Checker.IsNumber(self.__ahead):
                # error
                Error.RaiseError(
                    self.__filePath,
                    self.__fileCode,
                    "invalid number format \"%s\"" % number,
                    line, 
                    colm,
                    self.__lineBefore,
                    self.__colmBefore
                )

            number += self.__NumberPart()
            ttype = Token.DBL
        

        if  self.__ahead in ("e", "E"):
            number += self.__MoveForward()

            if  self.__ahead in ("+", "-"):
                number += self.__MoveForward()

            if  not Checker.IsNumber(self.__ahead):
                # error
                Error.RaiseError(
                    self.__filePath,
                    self.__fileCode,
                    "invalid number format \"%s\"" % number,
                    line, 
                    colm,
                    self.__lineBefore,
                    self.__colmBefore
                )

            number += self.__NumberPart()
            ttype = Token.DBL

        return Token(
            ttype,
            number,
            line,
            colm,
            self.__lineBefore,
            self.__colmBefore
        )    


    def __NumberPart(self):
        part = ""
        while not self.__IsEof() and \
            Checker.IsNumber(self.__ahead):
            part += self.__MoveForward()
        
        return part
    

    def __HexPart(self):
        part = ""
        while not self.__IsEof() and \
            Checker.IsHex(self.__ahead):
            part += self.__MoveForward()
        
        return part
    

    def __OctPart(self):
        part = ""
        while not self.__IsEof() and \
            Checker.IsOct(self.__ahead):
            part += self.__MoveForward()
        
        return part
    

    def __BinPart(self):
        part = ""
        while not self.__IsEof() and \
            Checker.IsBin(self.__ahead):
            part += self.__MoveForward()
        
        return part


    def __MakeCharacter(self):
        line, colm = self.__line, self.__colm
        open, close = self.__MoveForward(), None

        character = ""
        close = self.__ahead

        if  not self.__IsEof() and (open != close):
            
            if  self.__ahead == "\\":
                character += self.__MoveForward()

                if  self.__ahead == "b":
                    character += "\b"

                elif self.__ahead == "n":
                    character += "\n"

                elif self.__ahead == "t":
                    character += "\t"

                elif self.__ahead == "r":
                    character += "\r"

                elif self.__ahead == "0":
                    character += "\0"
                
                elif self.__ahead == "\"":
                    character += "\""
                
                elif self.__ahead == "\'":
                    character += "\'"
            
                self.__MoveForward()

            else:
                string += self.__MoveForward()
            
            close = self.__ahead
        

        if  open != close:
            # error
            Error.RaiseError(
                self.__filePath,
                self.__fileCode,
                "unterminated character literal",
                line, 
                colm,
                self.__lineBefore,
                self.__colmBefore
            )
        
        self.__MoveForward()

        if  len(character) != 1:
            # error
            Error.RaiseError(
                self.__filePath,
                self.__fileCode,
                "invalid character literal \"%s\"" % character,
                line, 
                colm,
                self.__lineBefore,
                self.__colmBefore
            )
        
        return Token(
            Token.CHR,
            string,
            line,
            colm,
            self.__lineBefore,
            self.__colmBefore
        )


    def __MakeString(self):
        line, colm = self.__line, self.__colm
        open, close = self.__MoveForward(), None

        string = ""
        close = self.__ahead

        while not self.__IsEof() and (open != close):
            
            if  self.__ahead == "\n":
                break
            
            if  self.__ahead == "\\":
                string += self.__MoveForward()

                if  self.__ahead == "b":
                    string += "\b"

                elif self.__ahead == "n":
                    string += "\n"

                elif self.__ahead == "t":
                    string += "\t"

                elif self.__ahead == "r":
                    string += "\r"

                elif self.__ahead == "0":
                    string += "\0"
                
                elif self.__ahead == "\"":
                    string += "\""
                
                elif self.__ahead == "\'":
                    string += "\'"
            
                self.__MoveForward()

            else:
                string += self.__MoveForward()
            
            close = self.__ahead
        

        if  open != close:
            # error
            Error.RaiseError(
                self.__filePath,
                self.__fileCode,
                "unterminated string literal",
                line, 
                colm,
                self.__lineBefore,
                self.__colmBefore
            )
        
        self.__MoveForward()
        
        return Token(
            Token.STR,
            string,
            line,
            colm,
            self.__lineBefore,
            self.__colmBefore
        )


    def __MakeOperator(self):
        line, colm = self.__line, self.__colm
        operator = ""

        if  self.__ahead == "(" or \
            self.__ahead == "(" or \
            self.__ahead == "[" or \
            self.__ahead == "]" or \
            self.__ahead == "{" or \
            self.__ahead == "}" or \
            self.__ahead == ";":
            operator = self.__MoveForward()
        
        elif self.__ahead == "*":
            operator = self.__MoveForward()

            if  self.__ahead == "*":
                operator += self.__MoveForward()

            if  self.__ahead == "=":
                operator += self.__MoveForward()
        
        elif self.__ahead == "/":
            operator = self.__MoveForward()

            if  self.__ahead == "=":
                operator += self.__MoveForward()
        
        elif self.__ahead == "+":
            operator = self.__MoveForward()

            if  self.__ahead == "+":
                operator += self.__MoveForward()

            elif self.__ahead == "=":
                operator += self.__MoveForward()
        
        elif self.__ahead == "-":
            operator = self.__MoveForward()

            if  self.__ahead == "-":
                operator += self.__MoveForward()

            elif self.__ahead == "=":
                operator += self.__MoveForward()
        
        elif self.__ahead == "<":
            operator = self.__MoveForward()

            if  self.__ahead == "<":
                operator += self.__MoveForward()

            if self.__ahead == "=":
                operator += self.__MoveForward()

        elif self.__ahead == ">":
            operator = self.__MoveForward()

            if  self.__ahead == ">":
                operator += self.__MoveForward()

            if self.__ahead == "=":
                operator += self.__MoveForward()
        
        elif self.__ahead == "!":
            operator = self.__MoveForward()

            if  self.__ahead == "=":
                operator += self.__MoveForward()
        
        elif self.__ahead == "=":
            operator = self.__MoveForward()

            if  self.__ahead == "=":
                operator += self.__MoveForward()
        
        elif self.__ahead == "&":
            operator = self.__MoveForward()

            if self.__ahead == "&":
                operator += self.__MoveForward()
            
            elif self.__ahead == "=":
                operator += self.__MoveForward()
        
        elif self.__ahead == "|":
            operator = self.__MoveForward()

            if  self.__ahead == "|":
                operator += self.__MoveForward()

            elif self.__ahead == "=":
                operator += self.__MoveForward()
        
        elif self.__ahead == "^":
            operator = self.__MoveForward()

            if self.__ahead == "=":
                operator += self.__MoveForward()

        elif self.__ahead == "?":
            operator = self.__MoveForward()

            if  self.__ahead == "?":
                operator += self.__MoveForward()

            elif self.__ahead == ".":
                operator += self.__MoveForward()
        
        elif self.__ahead == ":":
            operator = self.__MoveForward()

            if  self.__ahead == ":":
                operator += self.__MoveForward()
        
        else:
            # error
            Error.RaiseError(
                self.__filePath,
                self.__fileCode,
                "invalid or unknown token \"%s\"" % self.__ahead,
                line, 
                colm,
                self.__lineBefore,
                self.__colmBefore
            )

        return Token(
            Token.SYM,
            operator,
            line,
            colm,
            self.__lineBefore,
            self.__colmBefore
        )


    def __MakeEof(self):
        return Token(
            Token.EOF, 
            "eof", 
            self.__line, 
            self.__colm, 
            self.__lineBefore, 
            self.__colmBefore + 3
        )


    def nextToken(self):
        
        while not self.__IsEof():
            
            if  Checker.IsIgnoreable(self.__ahead):
                self.__Forward()

            elif Checker.IsIdentifier(self.__ahead):
                return self.__MakeIdentifier()
            
            elif Checker.IsNumber(self.__ahead):
                return self.__MakeNumber()

            elif Checker.IsCharacter(self.__ahead):
                return self.__MakeCharacter()
            
            elif Checker.IsString(self.__ahead):
                return self.__MakeString()
        
            else:
                return self.__MakeOperator()

        return self.__MakeEof()


    def __IsEof(self):
        return self.__index >= len(self.__fileCode)