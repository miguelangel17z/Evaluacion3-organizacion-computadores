from Parser import Parser
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

def main():
    vm = VMTranslator()
    if len(sys.argv) != 2:
        print("Escriba correctamente los argumentos")
    else:
        file = vm.readFileVM(sys.argv[1])
        ps = Parser(file)
        while(ps.hasMoreLines()):
            ps.advance()
            print(ps.commanType())
            print("Arg1: ", ps.arg1,"| Arg2: ", ps.arg2)

    

if __name__ == "__main__":
    main()


