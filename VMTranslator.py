import sys
import os
from Parser import Parser
from CodeWriter import CodeWriter

def clean_lines(lines):
    cleaned = []
    for line in lines:
        line = line.strip()
        if "//" in line:
            line = line[:line.index("//")]
        if line != "":
            cleaned.append(line)
    return cleaned

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
        if not path.endswith(".vm"):
            print("Si pasas un archivo, debe ser .vm")
            return
        files = [path]
        out_asm = path[:-3] + "asm"

    # Crear CodeWriter (él escribe directo al .asm)
    cw = CodeWriter(out_asm)

    # Bootstrap si es carpeta (múltiples archivos => punto de entrada Sys.init)
    if os.path.isdir(path):
        cw.writeBootstrap()

    # Traducir cada archivo .vm
    for vmfile in files:
        cw.setFileName(vmfile)  # importante para símbolos "static"
        with open(vmfile, "r") as f:
            lines = clean_lines(f.readlines())

        ps = Parser(lines)
        while ps.hasMoreLines():
            ps.advance()
            ctype = ps.commandType()

            if ctype == "C_ARITHMETIC":
                cw.writeArithmetic(ps.arg1)
            elif ctype in ("C_PUSH", "C_POP"):
                cw.writePushPop(ctype, ps.arg1, ps.arg2)
            elif ctype == "C_LABEL":
                cw.writeLabel(ps.arg1)
            elif ctype == "C_GOTO":
                cw.writeGoto(ps.arg1)
            elif ctype == "C_IF":
                cw.writeIf(ps.arg1)
            elif ctype == "C_FUNCTION":
                cw.writeFunction(ps.arg1, ps.arg2)
            elif ctype == "C_CALL":
                cw.writeCall(ps.arg1, ps.arg2)
            elif ctype == "C_RETURN":
                cw.writeReturn()

    cw.close()
    print(f"Archivo generado: {out_asm}")

if __name__ == "__main__":
    main()
