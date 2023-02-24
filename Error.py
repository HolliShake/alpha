from sys import stderr, exit

class Error:

    @staticmethod
    def ShowAndExit(context, message):
        print("[LangError] -> " + context + ": " + message + ".", file=stderr)
        exit(1)
    


    @staticmethod
    def RaiseError(filePath, fileCode, message, lineStart, colmStart, lineEnded, colmEnded):
        headerMessage = "[%s:%d:%d] %s." % (filePath, lineStart, lineEnded, message)

        PADDING = 3
        lines = fileCode.split("\n")

        start = (
            (lineStart - PADDING) 
            if  (lineStart - PADDING) >= 1
            else lineStart 
        )

        ended = (
            (lineEnded + PADDING) 
            if  (lineEnded + PADDING) < len(lines)
            else lineEnded
        )

        location = lines[(start - 1):ended]

        view = ""

        for idx in range(len(location)):
            ln = location[idx]

            space = " " * (len(str(ended)) - len(str(start + idx)))
            view += ("%s%d" % (space, (start + idx))) + " | "

            if  lineStart != lineEnded:
                if  (start + idx) >= start and (start + idx) <= ended:
                    view += " ~ "

                view += ln
            
            else:
                cidx = 0
                while cidx < len(ln):
                    if  cidx != (colmStart - 1):
                        view += ln[cidx]
                        cidx += 1
                    else:
                        view += "{{error here -> \""

                        while cidx != colmEnded:
                            view += ln[cidx]
                            cidx += 1
                        
                        view += "\"}}"
                        break
                
                for _ in range(cidx, len(ln)):
                    view += ln[_]

            if  idx < (len(location) - 1):
                view += "\n"

        error = headerMessage + "\n" + view
        print(error, file=stderr)
        exit(1)