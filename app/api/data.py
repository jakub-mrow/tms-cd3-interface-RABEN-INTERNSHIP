# <----------------------------------------------->
# setting up data object to store repeating values
# for requests like cookies or token
# <----------------------------------------------->
class Data:
    def __init__(self):
        self.fileName = ""
        self.filePath = ""
        self.cookies = ""
        self.token = ""
        self.indexes = {}
        self.categoryName = ""
        self.documentID = ""
        self.documentClass = ""
        self.outputFormat = {
            "categoryValues": [
                [
                    
                ]
            ]
        }

    # pass cookies from headers
    def setCookies(self, rawCookie):
        splitted = rawCookie.split()
        returnCookie = ""
        for item in splitted:
                if "cd3session" in item:
                        returnCookie += item
                        returnCookie+= " "
                if "core" in item:
                        returnCookie += item[:-1]
        self.cookies = returnCookie

    def setToken(self, token):
        self.token = "cd3session {}".format(token)