from Parser import Parser
from CodeWriter import CodeWriter
import sys
import os
from Parser import Parser
from CodeWriter import CodeWriter

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
    if len(sys.argv) != 2:
        print("Uso: python VMTranslator.py <archivo.vm | carpeta>")
        return

    path = sys.argv[1]

    # Descubrir archivos de entrada y archivo de salida
    if os.path.isdir(path):
        files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".vm")]
        if not files:
            print("No se encontraron .vm en la carpeta.")
            return
        out_asm = os.path.join(path, os.path.basename(path) + ".asm")
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
            

    cw.close()
    print(f"Archivo generado: {out_asm}")

if __name__ == "__main__":
    main()
