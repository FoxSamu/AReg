"""
Commands
> | move right on the memory register
< | move left on the memory register
+ | increase target registry by one
- | decrease target registry by one
, | take target and store as ASCII hex to byte. If it doesn’t exist in ASCII, return 0
. | print current memory register as ASCII, byte to hex, in target cell 
[ | jump to matching ] if memory register = 0 (begin loop command, looping until final value = 0)
] | jump to matching [ if memory register != 0 (end 0 loop command)
( | jump to matching ) if memory register = A Register (begin loop command, looping until final value = the A Register)
) | jump to matching ( if memory register != A Register (end A Register loop command)
^ | swaps target from memory tape to A Register and visa versa
; | takes the value in the target cell and puts it in the recipient cell. Does not delete the value in the target cell
: | swaps the values in the target cell and recipient cell with each other
! | print current memory register as decimal number
_ | prints a system dependent newline
"""

import sys

# Set to True if debug logging must be enabled (prints every executed command)
DEBUG = False

# Max value for a register
BYTE_MAX = (1<<8) - 1

# All commands as numbers
MOV_R = 0  # >
MOV_L = 1  # <
INCR  = 2  # +
DECR  = 3  # -
READ  = 4  # ,
WRITE = 5  # .
JMPF0 = 6  # [
JMPB0 = 7  # ]
JMPFA = 8  # (
JMPBA = 9  # )
FLIP  = 10 # ^
COPY  = 11 # ;
SWAP  = 12 # :
WRNUM = 13 # !
NEWL  = 14 # _

# Character to command ID
COMMANDS = {
    ">": MOV_R,
    "<": MOV_L,
    "+": INCR,
    "-": DECR,
    ",": READ,
    ".": WRITE,
    "[": JMPF0,
    "]": JMPB0,
    "(": JMPFA,
    ")": JMPBA,
    "^": FLIP,
    ";": COPY,
    ":": SWAP,
    "!": WRNUM,
    "_": NEWL
}

# Command ID to name (for debugging purposes)
NAMES = [
    "mov_r",
    "mov_l",
    "incr",
    "decr",
    "read",
    "write",
    "jmpf0",
    "jmpb0",
    "jmpfa",
    "jmpba",
    "flip",
    "copy",
    "swap",
    "wrnum",
    "newl"
]

# Parses AReg code and returns a list of all the commands, optionally with a jump location
def parse(text):
    length = len(text)
    code = []
    stack0 = []
    stackA = []

    stacks = {
        "[": stack0,
        "]": stack0,
        "(": stackA,
        ")": stackA
    }
    comment_mode = False
    for i in range(length):
        ch = text[i]
        if comment_mode:
            if ch == "\n" or ch == "\r":
                comment_mode = False
        else:
            if ch == "#":
                comment_mode = True
            elif ch in COMMANDS:
                cmd = COMMANDS[ch]
                
                if ch in "><+-,.^;:!_":  # Non-jumping command
                    code.append([cmd])
                    
                elif ch in "[(":       # Jump forward command
                    stacks[ch].append(len(code))
                    code.append([cmd])
                    
                elif ch in "])":       # Jump backward command
                    stack = stacks[ch]

                    if len(stack) > 0:
                        fpos = stacks[ch].pop()
                        bpos = len(code)
                        code.append([cmd, fpos])
                        code[fpos].append(bpos)
                    else:
                        code.append([cmd])

    return code


# Utility to read one char at a time from input lines
current_input = None
current_input_pos = 0

def readchar():
    global current_input
    global current_input_pos
    
    while current_input == None:
        current_input = sys.stdin.readline()
        current_input_pos = 0
        if current_input_pos > len(current_input):
            current_input = None

    c = current_input[current_input_pos]
    current_input_pos += 1
    if current_input_pos > len(current_input):
        current_input = None

    o = ord(c)
    if o > BYTE_MAX: o = 0
    return o

# Runtime, has a couple of functions that map to instructions
# Some instructions have two functions, one for AReg mode and one for Memory mode
class Runtime:
    def __init__(self, code, tapelen):
        self.code = code         # Code (parsed)
        self.tapelen = tapelen   # Tape length
        self.proglen = len(code) # Program length
        self.tape = [0]*tapelen  # Tape
        self.areg = 0            # A Register
        self.memptr = 0          # Memory pointer
        self.progptr = 0         # Program pointer
        self.in_areg = False     # A Register mode

    # Debug
    def log(self, *args):
        if DEBUG:
            print(self.progptr, *args)

    # >
    def mov_r(self, insn):
        self.memptr += 1
        if self.memptr >= self.tapelen:
            self.memptr = 0
        if DEBUG: print("mov_r: ", self.memptr)

    # <  
    def mov_l(self, insn):
        self.memptr -= 1
        if self.memptr < 0:
            self.memptr = self.tapelen - 1
        if DEBUG: print("mov_l: ", self.memptr)

    # + AReg Mode
    def incr_areg(self, insn):
        self.areg += 1
        if self.areg > BYTE_MAX:
            self.areg = 0
        if DEBUG: print("incr_areg: ", self.areg)
        
    # - AReg Mode
    def decr_areg(self, insn):
        self.areg -= 1
        if self.areg < 0:
            self.areg = BYTE_MAX
        if DEBUG: print("decr_areg: ", self.areg)

    # + Memory Mode
    def incr_mem(self, insn):
        tape = self.tape
        memptr = self.memptr
        tape[memptr] += 1
        if tape[memptr] > BYTE_MAX:
            tape[memptr] = 0
        if DEBUG: print("incr_mem: ", tape[memptr], "at", memptr)
        
    # - Memory Mode
    def decr_mem(self, insn):
        tape = self.tape
        memptr = self.memptr
        tape[memptr] -= 1
        if tape[memptr] < 0:
            tape[memptr] = BYTE_MAX
        if DEBUG: print("decr_mem: ", tape[memptr], "at", memptr)
        
    # , AReg Mode
    def read_areg(self, insn):
        self.areg = readchar()
        if DEBUG: print("read_areg: ", self.areg)
        
    # , Memory Mode
    def read_mem(self, insn):
        self.tape[self.memptr] = readchar()
        if DEBUG: print("read_mem: ", self.tape[self.memptr], "at", self.memptr)
        
    # . AReg Mode
    def write_areg(self, insn):
        sys.stdout.write(chr(self.areg))
        if DEBUG: print("write_areg: ", self.areg)
        
    # . Memory Mode
    def write_mem(self, insn):
        sys.stdout.write(chr(self.tape[self.memptr]))
        if DEBUG: print("write_mem: ", self.tape[self.memptr], "at", self.memptr)
        
    # ! AReg Mode
    def wrnum_areg(self, insn):
        sys.stdout.write(str(self.areg))
        if DEBUG: print("wrnum_areg: ", self.areg)
        
    # ! Memory Mode
    def wrnum_mem(self, insn):
        sys.stdout.write(str(self.tape[self.memptr]))
        if DEBUG: print("wrnum_mem: ", self.tape[self.memptr], "at", self.memptr)
        
    # _
    def newl(self, insn):
        print()
        if DEBUG: print("newl")

    # [
    def jmpf0(self, insn):
        if self.tape[self.memptr] == 0:
            if len(insn) == 1:
                self.progptr = self.proglen
            else:
                self.progptr = insn[1]
            if DEBUG: print("jmpf0: jumped to:", self.progptr, "- memory:", self.tape[self.memptr], "at", self.memptr)
        elif DEBUG: print("jmpf0: not jumped - memory:", self.tape[self.memptr], "at", self.memptr)

    # ]
    def jmpb0(self, insn):
        if self.tape[self.memptr] != 0:
            if len(insn) == 1:
                self.progptr = 0
            else:
                self.progptr = insn[1]
            if DEBUG: print("jmpb0: jumped to:", self.progptr, "- memory:", self.tape[self.memptr], "at", self.memptr)
        elif DEBUG: print("jmpb0: not jumped - memory:", self.tape[self.memptr], "at", self.memptr)


    # (
    def jmpfa(self, insn):
        if self.tape[self.memptr] == self.areg:
            if len(insn) == 1:
                self.progptr = self.proglen
            else:
                self.progptr = insn[1]
            if DEBUG: print("jmpfa: jumped to:", self.progptr, "- memory:", self.tape[self.memptr], "at", self.memptr, "- areg:", self.areg)
        elif DEBUG: print("jmpfa: not jumped - memory:", self.tape[self.memptr], "at", self.memptr, "- areg:", self.areg)

    # )
    def jmpba(self, insn):
        if self.tape[self.memptr] != self.areg:
            if len(insn) == 1:
                self.progptr = 0
            else:
                self.progptr = insn[1]
            if DEBUG: print("jmpba: jumped to:", self.progptr, "- memory:", self.tape[self.memptr], "at", self.memptr, "- areg:", self.areg)
        elif DEBUG: print("jmpba: not jumped - memory:", self.tape[self.memptr], "at", self.memptr, "- areg:", self.areg)

    # ^
    def flip(self, insn):
        self.in_areg = not self.in_areg
        if DEBUG: print("flip: ", self.in_areg)

    # ; AReg Mode     
    def copy_areg(self, insn):
        self.areg = self.tape[self.memptr]
        if DEBUG: print("copy_areg: ", self.areg, "from", self.memptr)
            
    # ; Memory Mode    
    def copy_mem(self, insn):
        self.tape[self.memptr] = self.areg
        if DEBUG: print("copy_areg: ", self.areg, "to", self.memptr)

    # :
    def swap(self, insn):
        self.tape[self.memptr], self.areg = self.areg, self.tape[self.memptr]
        if DEBUG: print("swap: areg: ", self.areg, "- memory:", self.tape[self.memptr], "at", self.memptr)
        
    
# Runs parsed code, given a fixed tape length
def run(code, tapelen):
    rt = Runtime(code, tapelen)

    # Map command code to instruction method of Runtime, for both AReg mode and Memory mode
    # This avoids a large if statement
    insns_areg = [
        rt.mov_r, rt.mov_l,
        rt.incr_areg, rt.decr_areg,
        rt.read_areg, rt.write_areg,
        rt.jmpf0, rt.jmpb0,
        rt.jmpfa, rt.jmpba,
        rt.flip, rt.copy_areg, rt.swap,
        rt.wrnum_areg,
        rt.newl
    ]
    insns_mem = [
        rt.mov_r, rt.mov_l,
        rt.incr_mem, rt.decr_mem,
        rt.read_mem, rt.write_mem,
        rt.jmpf0, rt.jmpb0,
        rt.jmpfa, rt.jmpba,
        rt.flip, rt.copy_mem, rt.swap,
        rt.wrnum_mem,
        rt.newl
    ]
    insns_list = [insns_mem, insns_areg]

    # Run the program
    while rt.progptr < rt.proglen:
        insn = rt.code[rt.progptr]
        cmd = insn[0]

        insns = insns_list[int(rt.in_areg)]
        insns[cmd](insn)
        rt.progptr += 1

    if DEBUG:
        print("Finished", rt.tape)


# Prints program instructions with proper names and jump codes
def printcode(code):
    print("--- Code ---")
    n = 0
    for i in code:
        if len(i) == 1:
            print(n, NAMES[i[0]])
        else:
            print(n, NAMES[i[0]], i[1])
        n += 1

    
# Open and read file
filename = input("AReg file: ")
file = open(filename, "r")
text = str(file.read())
        
code = parse(text)

if DEBUG:
    printcode(code)

tape_length = int(input("Tape length (128 recommended): "))

if DEBUG:
    input("Debug mode: press enter to start")

run(code, tape_length)






