import sys
from Lexer import Lexer


def start(args):
    print(args)
    x = Lexer(0, "Hello.x", "\n\n\n\n\n\n\nhello ++ 0bffg fooc\n\n\n\n\n\n\n")
    tok = x.nextToken()

    while tok.tokenType != 0x07:
        print(tok)
        tok = x.nextToken()
    print(tok)

if  __name__ == "__main__":
    start(sys.argv)

