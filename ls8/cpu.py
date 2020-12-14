"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
HLT = 0b00000001

# SPRINT--------

CMP = 0b10100111
JEQ = 0b01010101
JMP = 0b01010100
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.fl = 0b00000000
        self.pc = 0

        self.branchtable = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            PUSH: self.push,
            POP: self.pop,

            # SPRINT--------

            JEQ: self. jeq,
            JMP: self.jmp,
            JNE: self.jne
        }

    def load(self):
        """Load a program into memory."""

        if (len(sys.argv)) != 2:
            print("usage: python3 ls8.py filename")
            sys.exit(1)

        address = 0

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    possible_number = line[:line.find('#')]
                    if possible_number == '':
                        continue

                    instruction = int(possible_number, 2)

                    self.ram[address] = instruction

                    address += 1

        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]

        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]

        # SPRINT--------------------------------

        elif op == CMP:
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001

            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100

            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010

        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def hlt(self, op_a, op_b):
        self.running = False

    def ldi(self, op_a, op_b):
        self.reg[op_a] = op_b

    def prn(self, op_a, op_b):
        print(self.reg[op_a])

    def push(self, op_a, op_b):
        self.reg[7] -= 1
        value = self.reg[op_a]
        SP = self.reg[7]
        self.ram_write(SP, value)

    def pop(self, op_a, op_b):
        SP = self.reg[7]
        value = self.ram_read(SP)
        self.reg[op_a] = value
        self.reg[7] += 1

    # SPRINT-----------------------

    def jmp(self, op_a, op_b):
        address = op_a
        self.pc = self.reg[address]

    def jeq(self, op_a, op_b):
        if self.fl == 0b00000001:
            address = op_a
            self.pc = self.reg[address]

    def jne(self, op_a, op_b):
        if self.fl != 0b00000001:
            address = op_a
            self.pc = self.reg[address]

    def run(self):
        """Run the CPU."""

        self.running = True

        while self.running:
            ir = self.ram_read(self.pc)

            op_a = self.ram_read(self.pc + 1)

            op_b = self.ram_read(self.pc + 2)

            num_operands = ir >> 6
            self.pc += 1 + num_operands

            is_alu_op = ((ir >> 5) & 0b001) == 1

            if is_alu_op:
                self.alu(ir, op_a, op_b)

            else:
                self.branchtable[ir](op_a, op_b)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
