class Parser:
    instructions = []
    pc = 0
    currentLine = ""
    arCommands = ["add", "sub" , "neg", "eq" , "gt" , "lt", "and", "or" , "not"]
    logCommands = ["pop", "push"]
    arg1= None
    arg2= None
     

    def __init__(self, lines):
        self.instructions = lines

    def hasMoreLines(self):
        return len(self.instructions)>0
            

    def advance(self):
        if(self.hasMoreLines()):
            self.currentLine = self.instructions[0]
            p = self.instructions.pop(0)
            
    
    def commanType(self):
        line = self.currentLine.split(" ")
        if line[0] in self.arCommands:
            self.arg1 = line[0]
            self.arg2 = None
            return "C_ARITHMETIC"
        if line[0] in self.logCommands:
            self.arg1 = line [1]
            self.arg2 = int(line[2])
            if line[0] == "pop":
                return "C_POP"
            else:
                return "C_PUSH"
        

    



