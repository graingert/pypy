from rpython.jit.tl.threadedcode import tla

code = [
    tla.CONST_N, 0, 0, 15, 160, 
    tla.DUP, 
    tla.CALL_ASSEMBLER, 14, 1, 
    tla.DUP, 
    tla.PRINT, 
    tla.POP1, 
    tla.POP1, 
    tla.EXIT, 
    tla.DUPN, 1, 
    tla.CONST_INT, 1, 
    tla.LT, 
    tla.JUMP_IF, 39, 
    tla.DUPN, 1, 
    tla.CONST_INT, 1, 
    tla.SUB, 
    tla.DUP, 
    tla.CALL_ASSEMBLER, 14, 1, 
    tla.DUPN, 3, 
    tla.DUPN, 1, 
    tla.MUL, 
    tla.POP1, 
    tla.POP1, 
    tla.JUMP, 41, 
    tla.CONST_INT, 1, 
    tla.RET, 1, 
]