class Parser:
    instructions = []
    currentLine = ""
    arCommands = ["add","sub","neg","eq","gt","lt","and","or","not"]
    stackCommands = ["pop","push"]
    arg1 = None
    arg2 = None

    def __init__(self, lines):
        self.instructions = list(lines)  # copia
        self.currentLine = ""
        self.arg1 = None
        self.arg2 = None

    def hasMoreLines(self):
        return len(self.instructions) > 0

    def advance(self):
        if self.hasMoreLines():
            self.currentLine = self.instructions.pop(0)
            self.arg1 = None
            self.arg2 = None

    def commandType(self):
        parts = self.currentLine.split()
        op = parts[0]

        # Aritmética
        if op in self.arCommands:
            self.arg1 = op
            self.arg2 = None
            return "C_ARITHMETIC"

        # push/pop
        if op in self.stackCommands:
            self.arg1 = parts[1]                # segmento
            self.arg2 = int(parts[2])           # índice
            return "C_PUSH" if op == "push" else "C_POP"

        # label / goto / if-goto
        if op == "label":
            self.arg1 = parts[1]
            return "C_LABEL"
        if op == "goto":
            self.arg1 = parts[1]
            return "C_GOTO"
        if op == "if-goto":
            self.arg1 = parts[1]
            return "C_IF"

        # function / call / return
        if op == "function":
            self.arg1 = parts[1]                # nombre función
            self.arg2 = int(parts[2])           # nLocals
            return "C_FUNCTION"
        if op == "call":
            self.arg1 = parts[1]                # nombre función
            self.arg2 = int(parts[2])           # nArgs
            return "C_CALL"
        if op == "return":
            return "C_RETURN"

        # Si cae aquí, hay una instrucción no soportada
        raise ValueError(f"Comando VM no reconocido: {self.currentLine}")

