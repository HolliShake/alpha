


class Token:

    IDN = 0x01
    OTH = 0x02
    INT = 0x03
    DBL = 0x04
    CHR = 0x05
    STR = 0x06
    EOF = 0x07

    def __init__(self,
        tokenType, 
        tokenValue,
        lineStart,
        colmStart,
        lineEnded,
        colmEnded
    ):
        self.tokenType  = tokenType
        self.tokenValue = tokenValue
        self.lineStart  = lineStart
        self.colmStart  = colmStart
        self.lineEnded  = lineEnded
        self.colmEnded  = colmEnded


    def __str__(self):
        return "Token(type: %d, symbol: %s, appearance: [%d:%d ~ %d:%d])" % (self.tokenType, repr(self.tokenValue), self.lineStart, self.colmStart, self.lineEnded, self.colmEnded)