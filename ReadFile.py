from .Error import Error


class ReadFile:

    @staticmethod
    def Read(filePath):
        try:
            fileObject = open(filePath, "r", encoding="utf8")
            return (
                fileObject.read(), 
                ("frozen" in filePath.split("."))
            )
        except:
            Error.ShowAndExit("ReadFile::Read", "File not found \"%s\" (No such file or dir)" % filePath)

