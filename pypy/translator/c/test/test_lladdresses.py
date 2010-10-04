import py, sys
from pypy.rpython.lltypesystem.llmemory import *
from pypy.annotation.model import SomeAddress, SomeChar
from pypy.translator.c.test.test_genc import compile
from pypy.rlib.objectmodel import free_non_gc_object

def test_null():
    def f():
        return NULL - NULL
    fc = compile(f, [])

def test_convert_to_bool():
    def f(x):
        if x:
            return bool(NULL)
        else:
            return bool(NULL + 1)
    fc = compile(f, [int])
    res = fc(1)
    assert isinstance(res, bool) and not res
    res = fc(0)
    assert isinstance(res, bool) and res

def test_memory_access():
    def f(value):
        addr = raw_malloc(16)
        addr.signed[0] = value
        result = addr.signed[0]
        raw_free(addr)
        return result
    fc = compile(f, [int])
    res = fc(42)
    assert res == 42
    res = fc(1)
    assert res == 1
    
def test_memory_float():
    S = lltype.GcStruct("S", ("x", lltype.Float), ("y", lltype.Float))
    offset = FieldOffset(S, 'x')
    offsety = FieldOffset(S, 'y')
    def f(value):
        s = lltype.malloc(S)
        s.x = 123.2
        a = cast_ptr_to_adr(s)
        b = a + offset
        assert b.float[0] == 123.2
        b.float[0] = 234.1
        (a + offsety).float[0] = value
        assert s.x == 234.1
        return s.x + value
    fc = compile(f, [float])
    res = fc(42.42)
    assert res == f(42.42)

def test_pointer_arithmetic():
    def f(offset, char):
        addr = raw_malloc(10000)
        same_offset = (addr + 2 * offset - offset) - addr 
        addr.char[offset] = char
        result = (addr + same_offset).char[0]
        raw_free(addr)
        return result
    fc = compile(f, [int, SomeChar()])
    res = fc(10, "c")
    assert res == "c"
    res = fc(12, "x")
    assert res == "x"

def test_pointer_arithmetic_inplace():
    def f(offset, char):
        addr = raw_malloc(10000)
        addr += offset
        addr.char[-offset] = char
        addr -= offset
        result = addr.char[0]
        raw_free(addr)
        return result
    fc = compile(f, [int, SomeChar()])
    res = fc(10, "c")
    assert res == "c"

def test_raw_memcopy():
    def f():
        addr = raw_malloc(100)
        addr.signed[0] = 12
        (addr + 10).signed[0] = 42
        (addr + 20).char[0] = "a"
        addr1 = raw_malloc(100)
        raw_memcopy(addr, addr1, 100)
        result = addr1.signed[0] == 12
        result = result and (addr1 + 10).signed[0] == 42
        result = result and (addr1 + 20).char[0] == "a"
        raw_free(addr)
        raw_free(addr1)
        return result
    fc = compile(f, [])
    res = fc()
    assert res

def test_raw_memmove():
    def f():
        addr = raw_malloc(100)
        addr.signed[0] = 12
        (addr + 10).signed[0] = 42
        raw_memmove(addr, addr + 4, 96)
        result = (addr + 4).signed[0] + (addr + 14).signed[0]
        raw_free(addr)
        return result
    fc = compile(f, [])
    res = fc()
    assert res

def test_pointer_comparison():
    def f():
        result = 0
        addresses = [raw_malloc(1), NULL]
        for addr1 in addresses:
            addr2 = addr1 + 1
            result = result * 2 + int(addr1 == addr2)
            result = result * 2 + int(addr1 != addr2)
            result = result * 2 + int(addr1 <  addr2)
            result = result * 2 + int(addr1 <= addr2)
            result = result * 2 + int(addr1 >  addr2)
            result = result * 2 + int(addr1 >= addr2)
        raw_free(addresses[0])
        return result
    fc = compile(f, [])
    res = fc()
    assert res == int('011100' * 2, 2)

def test_flavored_malloc_raw():
    class A(object):
        _alloc_flavor_ = "raw"
        def __init__(self, val):
            self.val = val
    def f(x):
        a = A(x + 1)
        result = a.val
        free_non_gc_object(a)
        return result
    fn = compile(f, [int])
    assert fn(1) == 2

def test_flavored_malloc_stack():
    class A(object):
        _alloc_flavor_ = "stack"
        def __init__(self, val):
            self.val = val
    def f(x):
        a = A(x + 1)
        result = a.val
        return result
    fn = compile(f, [int])
    assert fn(1) == 2

def test_gcref():
    if sys.platform == 'darwin':
        py.test.skip("'boehm' may crash")
    S = lltype.GcStruct("S", ("x", lltype.Signed))
    s = lltype.malloc(S)
    s.x = 123
    g1 = lltype.cast_opaque_ptr(GCREF, s)
    g2 = lltype.cast_opaque_ptr(GCREF, lltype.nullptr(S))
    def f2(x):
        if x > 0:
            return g1
        else:
            return g2
    def f(x):
        gref = f2(x)
        g = lltype.cast_opaque_ptr(lltype.Ptr(S), gref)
        if g:
            return g.x
        else:
            return -42
    fn = compile(f, [int], gcpolicy='boehm')
    assert fn(3) == 123
    assert fn(-3) == -42

def test_cast_adr_to_int():
    S = lltype.Struct("S", ("x", lltype.Signed))
    s = lltype.malloc(S, immortal=True)
    adr = cast_ptr_to_adr(s)
    def f(n):
        i = cast_adr_to_int(adr)
        if n > 10:
            adr2 = adr
        else:
            adr2 = NULL
        print "hello world"     # prevent constant-folding
        j = cast_adr_to_int(adr2)
        return i - j
    fc = compile(f, [int])
    res = fc(42)
    assert res == 0

def test_cast_int_to_adr():
    S = lltype.Struct("S", ("x", lltype.Signed))
    s = lltype.malloc(S, immortal=True)
    s.x = 42
    integer = cast_adr_to_int(cast_ptr_to_adr(s), mode="symbolic")
    def f(n):
        if n > 1:
            i = integer
        else:
            i = 123   # nonsense, but never used
        print "hello world"     # prevent constant-folding
        adr = cast_int_to_adr(i)
        s = cast_adr_to_ptr(adr, lltype.Ptr(S))
        return s.x
    fc = compile(f, [int])
    res = fc(5)
    assert res == 42

def test_dict_of_addresses():
    TP = lltype.Struct('x')
    a = lltype.malloc(TP, flavor='raw', immortal=True)
    b = lltype.malloc(TP, flavor='raw', immortal=True)

    def f(i):
        d = {}
        d[cast_ptr_to_adr(a)] = 123
        d[cast_ptr_to_adr(b)] = 456
        if i > 5:
            key = cast_ptr_to_adr(a)
        else:
            key = cast_ptr_to_adr(b)
        return d[key]

    fc = compile(f, [int])
    res = fc(-77)
    assert res == 456
    res = fc(77)
    assert res == 123


##class TestHiddenGcRef32(StandaloneTests):

##    def setup_class(cls):
##        from pypy.config.translationoption import IS_64_BITS
##        if 0:# not IS_64_BITS:
##            py.test.skip("only for 64-bits")

##    def test_hiddengcref32(self):
##        from pypy.rpython.lltypesystem.lloperation import llop
##        S = lltype.GcStruct('S', ('x', lltype.Signed),
##                                 ('y', HiddenGcRef32))
##        prebuilt = lltype.malloc(S, immortal=True)
##        prebuilt2 = lltype.malloc(S, immortal=True)
##        prebuilt.x = 42
##        prebuilt2.x = 53
##        prebuilt.y = llop.hide_into_adr32(HiddenGcRef32, prebuilt2)
##        prebuilt2.y = llop.hide_into_adr32(HiddenGcRef32, prebuilt)

##        def check(a, b):
##            p = llop.show_from_adr32(lltype.Ptr(S), a.y)
##            assert p == b

##        def f(argv):
##            assert prebuilt.x == 42
##            assert prebuilt2.x == 53
##            check(prebuilt, prebuilt2)
##            check(prebuilt2, prebuilt)
##            p = lltype.malloc(S)
##            p.y = llop.hide_into_adr32(HiddenGcRef32, prebuilt)
##            prebuilt2.y = llop.hide_into_adr32(HiddenGcRef32, p)
##            check(p, prebuilt)
##            check(prebuilt2, p)
##            check(prebuilt, prebuilt2)
##            return 0

##        fc = self.compile(f)
##        res = fc([])
##        assert res == 0
