from Parser import Parser
from CodeWriter import CodeWriter
import sys

class VMTranslator:
    def readFileVM(self, name):
        lines = []
        with open(name, "r") as f:
            lines = f.readlines()
        cleaned_lines = self.clean_lines(lines)

        return cleaned_lines

    def clean_lines(self, lines):
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if "//" in line:
                line = line[:line.index("//")]
            cleaned_lines.append(line)
        cleaned_lines = [x for x in cleaned_lines if x != ""]
        return cleaned_lines
    
    def setFileName(self, filename):
        return filename.replace('.vm', '.asm')
        




def main():
    vm = VMTranslator()
    if len(sys.argv) != 2:
        print("Escriba correctamente los argumentos")
    else:
        file = vm.readFileVM(sys.argv[1])
        ps = Parser(file)
        cw = CodeWriter(vm.setFileName(sys.argv[1]))
        while(ps.hasMoreLines()):
            ps.advance()
            cmd = ps.commanType()
            if cmd == "C_ARITHMETIC":
                cw.writeArithmetic(ps.arg1)
            elif cmd == "C_PUSH" or cmd == "C_POP":
                cw.writePushPop(cmd, ps.arg1, ps.arg2)
            

    

if __name__ == "__main__":
    main()


