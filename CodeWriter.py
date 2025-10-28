class CodeWriter:

    def __init__(self, output_file):
        self.output = open(output_file, 'w')
        self.current_file = ""
        self.label_counter = 0
        self.current_function = ""

    def setFileName(self, filename):
        import os
        # Solo nombre base sin extensión, p.ej. "Main"
        self.current_file = os.path.splitext(os.path.basename(filename))[0]


    def writeArithmetic(self, command):
        """Escribe código Assembly para comandos aritméticos"""
        code = []
        code.append('// ' + command)

        # Comandos binarios
        if command in ['add', 'sub', 'and', 'or']:
            code.append('@SP')
            code.append('AM=M-1')
            code.append('D=M')
            code.append('A=A-1')

            if command == 'add':
                code.append('M=D+M')
            elif command == 'sub':
                code.append('M=M-D')
            elif command == 'and':
                code.append('M=D&M')
            elif command == 'or':
                code.append('M=D|M')

        elif command in ['neg', 'not']:
            code.append('@SP')
            code.append('A=M-1')
            if command == 'neg':
                code.append('M=-M')
            elif command == 'not':
                code.append('M=!M')

        # Comandos de comparación
        elif command in ['eq', 'gt', 'lt']:
            true_lbl = f"TRUE_{self.label_counter}"
            false_lbl = f"FALSE_{self.label_counter}"
            self.label_counter += 1

            code.append('@SP')
            code.append('AM=M-1')
            code.append('D=M')
            code.append('A=A-1')
            code.append('D=M-D')
            code.append('@' + true_lbl)

            if command == 'eq':
                code.append('D;JEQ')
            elif command == 'gt':
                code.append('D;JGT')
            elif command == 'lt':
                code.append('D;JLT')

            code.append('@SP')
            code.append('A=M-1')
            code.append('M=0')
            code.append('@' + false_lbl)
            code.append('0;JMP')
            code.append('(' + true_lbl + ')')
            code.append('@SP')
            code.append('A=M-1')
            code.append('M=-1')
            code.append('(' + false_lbl + ')')

        self.output.write('\n'.join(code) + '\n')

    def writePushPop(self, command, segment, index):
        """Escribe código Assembly para push/pop"""
        code = []
        code.append(f'// {command} {segment} {index}')

        if command == "C_PUSH":
            # Obtener valor en D
            if segment == "constant":
                code.append(f'@{index}')
                code.append('D=A')
            elif segment in ["local", "argument", "this", "that"]:
                seg_pointer = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
                code.append(f'@{seg_pointer[segment]}')
                code.append('D=M')
                code.append(f'@{index}')
                code.append('A=D+A')
                code.append('D=M')
            elif segment == "temp":
                code.append(f'@{5 + index}')
                code.append('D=M')
            elif segment == "pointer":
                ptr = "THIS" if index == 0 else "THAT"
                code.append(f'@{ptr}')
                code.append('D=M')
            elif segment == "static":
                code.append(f'@{self.current_file}.{index}')
                code.append('D=M')

            # Push D al stack
            code.append('@SP')
            code.append('A=M')
            code.append('M=D')
            code.append('@SP')
            code.append('M=M+1')

        elif command == "C_POP":
            if segment in ["local", "argument", "this", "that"]:
                seg_pointer = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
                # Calcular dirección
                code.append(f'@{seg_pointer[segment]}')
                code.append('D=M')
                code.append(f'@{index}')
                code.append('D=D+A')
                code.append('@R13')
                code.append('M=D')
                # Pop valor
                code.append('@SP')
                code.append('AM=M-1')
                code.append('D=M')
                # Guardar
                code.append('@R13')
                code.append('A=M')
                code.append('M=D')
            elif segment == "temp":
                code.append('@SP')
                code.append('AM=M-1')
                code.append('D=M')
                code.append(f'@{5 + index}')
                code.append('M=D')
            elif segment == "pointer":
                ptr = "THIS" if index == 0 else "THAT"
                code.append('@SP')
                code.append('AM=M-1')
                code.append('D=M')
                code.append(f'@{ptr}')
                code.append('M=D')
            elif segment == "static":
                code.append('@SP')
                code.append('AM=M-1')
                code.append('D=M')
                code.append(f'@{self.current_file}.{index}')
                code.append('M=D')

        self.output.write('\n'.join(code) + '\n')

    def writeLabel(self, label):
        """Escribe un label"""
        self.output.write(f'({self.current_function}${label})\n')

    def writeGoto(self, label):
        """Escribe goto"""
        self.output.write(f'// goto {label}\n')
        self.output.write(f'@{self.current_function}${label}\n')
        self.output.write('0;JMP\n')

    def writeIf(self, label):
        """Escribe if-goto"""
        self.output.write(f'// if-goto {label}\n')
        self.output.write('@SP\n')
        self.output.write('AM=M-1\n')
        self.output.write('D=M\n')
        self.output.write(f'@{self.current_function}${label}\n')
        self.output.write('D;JNE\n')

    def writeFunction(self, function_name, num_locals):
        """Declara una función"""
        self.current_function = function_name
        self.output.write(f'// function {function_name} {num_locals}\n')
        self.output.write(f'({function_name})\n')

        # Inicializar locales en 0
        for i in range(num_locals):
            self.output.write('@SP\n')
            self.output.write('A=M\n')
            self.output.write('M=0\n')
            self.output.write('@SP\n')
            self.output.write('M=M+1\n')

    def writeCall(self, function_name, num_args):
        """Llama a una función"""
        ret_address = f"{self.current_function}$ret.{self.label_counter}"
        self.label_counter += 1

        self.output.write(f'// call {function_name} {num_args}\n')

        # Push return address
        self.output.write(f'@{ret_address}\n')
        self.output.write('D=A\n')
        self.output.write('@SP\n')
        self.output.write('A=M\n')
        self.output.write('M=D\n')
        self.output.write('@SP\n')
        self.output.write('M=M+1\n')

        # Push LCL, ARG, THIS, THAT
        for pointer in ['LCL', 'ARG', 'THIS', 'THAT']:
            self.output.write(f'@{pointer}\n')
            self.output.write('D=M\n')
            self.output.write('@SP\n')
            self.output.write('A=M\n')
            self.output.write('M=D\n')
            self.output.write('@SP\n')
            self.output.write('M=M+1\n')

        # ARG = SP - num_args - 5
        self.output.write('@SP\n')
        self.output.write('D=M\n')
        self.output.write(f'@{num_args + 5}\n')
        self.output.write('D=D-A\n')
        self.output.write('@ARG\n')
        self.output.write('M=D\n')

        # LCL = SP
        self.output.write('@SP\n')
        self.output.write('D=M\n')
        self.output.write('@LCL\n')
        self.output.write('M=D\n')

        # goto function
        self.output.write(f'@{function_name}\n')
        self.output.write('0;JMP\n')

        # (return address)
        self.output.write(f'({ret_address})\n')

    def writeReturn(self):
        """Retorna de una función"""
        self.output.write('// return\n')

        # FRAME = LCL
        self.output.write('@LCL\n')
        self.output.write('D=M\n')
        self.output.write('@R13\n')
        self.output.write('M=D\n')

        # RET = *(FRAME - 5)
        self.output.write('@5\n')
        self.output.write('A=D-A\n')
        self.output.write('D=M\n')
        self.output.write('@R14\n')
        self.output.write('M=D\n')

        # *ARG = pop()
        self.output.write('@SP\n')
        self.output.write('AM=M-1\n')
        self.output.write('D=M\n')
        self.output.write('@ARG\n')
        self.output.write('A=M\n')
        self.output.write('M=D\n')

        # SP = ARG + 1
        self.output.write('@ARG\n')
        self.output.write('D=M+1\n')
        self.output.write('@SP\n')
        self.output.write('M=D\n')

        # Restaurar THAT, THIS, ARG, LCL
        pointers = ['THAT', 'THIS', 'ARG', 'LCL']
        for i, ptr in enumerate(pointers, 1):
            self.output.write('@R13\n')
            self.output.write('D=M\n')
            self.output.write(f'@{i}\n')
            self.output.write('A=D-A\n')
            self.output.write('D=M\n')
            self.output.write(f'@{ptr}\n')
            self.output.write('M=D\n')

        # goto RET
        self.output.write('@R14\n')
        self.output.write('A=M\n')
        self.output.write('0;JMP\n')

    def writeBootstrap(self):
        """Inicializa el sistema"""
        self.output.write('// Bootstrap code\n')
        self.output.write('@256\n')
        self.output.write('D=A\n')
        self.output.write('@SP\n')
        self.output.write('M=D\n')
        self.writeCall('Sys.init', 0)

    def close(self):
        """Cierra el archivo"""
        self.output.close()