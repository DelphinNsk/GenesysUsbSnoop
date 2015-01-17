# interface
class Log:
    def __init__(self,filename, modules ):
        self.file = open(filename,"w")
        self.modules = modules;

    def log(self,module,message):
        if module in self.modules:
            text = "{:s}: {:s}\n".format(module,message)
            self.file.write(text)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
