from pypy.module._cffi_backend.newtype import _clean_cache

class AppTestFFIObj:
    spaceconfig = dict(usemodules=('_cffi_backend', 'array'))

    def teardown_method(self, meth):
        from pypy.module._cffi_backend.func import constant_ffi
        constant_ffi._cleanup_()
        _clean_cache(self.space)

    def test_ffi_new(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        p = ffi.new("int *")
        p[0] = -42
        assert p[0] == -42

    def test_ffi_subclass(self):
        import _cffi_backend as _cffi1_backend
        class FOO(_cffi1_backend.FFI):
            def __init__(self, x):
                self.x = x
        foo = FOO(42)
        assert foo.x == 42
        p = foo.new("int *")
        assert p[0] == 0

    def test_ffi_no_argument(self):
        import _cffi_backend as _cffi1_backend
        raises(TypeError, _cffi1_backend.FFI, 42)

    def test_ffi_cache_type(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        t1 = ffi.typeof("int **")
        t2 = ffi.typeof("int *")
        assert t2.item is t1.item.item
        assert t2 is t1.item
        assert ffi.typeof("int[][10]") is ffi.typeof("int[][10]")
        assert ffi.typeof("int(*)()") is ffi.typeof("int(*)()")

    def test_ffi_cache_type_globally(self):
        import _cffi_backend as _cffi1_backend
        ffi1 = _cffi1_backend.FFI()
        ffi2 = _cffi1_backend.FFI()
        t1 = ffi1.typeof("int *")
        t2 = ffi2.typeof("int *")
        assert t1 is t2

    def test_ffi_invalid(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        # array of 10 times an "int[]" is invalid
        raises(ValueError, ffi.typeof, "int[10][]")

    def test_ffi_docstrings(self):
        import _cffi_backend as _cffi1_backend
        # check that all methods of the FFI class have a docstring.
        check_type = type(_cffi1_backend.FFI.new)
        for methname in dir(_cffi1_backend.FFI):
            if not methname.startswith('_'):
                method = getattr(_cffi1_backend.FFI, methname)
                if isinstance(method, check_type):
                    assert method.__doc__, "method FFI.%s() has no docstring" % (
                        methname,)

    def test_ffi_NULL(self):
        import _cffi_backend as _cffi1_backend
        NULL = _cffi1_backend.FFI.NULL
        assert _cffi1_backend.FFI().typeof(NULL).cname == "void *"

    def test_ffi_no_attr(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        raises(AttributeError, "ffi.no_such_name")
        raises(AttributeError, "ffi.no_such_name = 42")
        raises(AttributeError, "del ffi.no_such_name")

    def test_ffi_string(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        p = ffi.new("char[]", init=b"foobar\x00baz")
        assert ffi.string(p) == b"foobar"

    def test_ffi_errno(self):
        import _cffi_backend as _cffi1_backend
        # xxx not really checking errno, just checking that we can read/write it
        ffi = _cffi1_backend.FFI()
        ffi.errno = 42
        assert ffi.errno == 42

    def test_ffi_alignof(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        assert ffi.alignof("int") == 4
        assert ffi.alignof("int[]") == 4
        assert ffi.alignof("int[41]") == 4
        assert ffi.alignof("short[41]") == 2
        assert ffi.alignof(ffi.new("int[41]")) == 4
        assert ffi.alignof(ffi.new("int[]", 41)) == 4

    def test_ffi_sizeof(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        assert ffi.sizeof("int") == 4
        raises(ffi.error, ffi.sizeof, "int[]")
        assert ffi.sizeof("int[41]") == 41 * 4
        assert ffi.sizeof(ffi.new("int[41]")) == 41 * 4
        assert ffi.sizeof(ffi.new("int[]", 41)) == 41 * 4

    def test_ffi_callback(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        assert ffi.callback("int(int)", lambda x: x + 42)(10) == 52
        assert ffi.callback("int(*)(int)", lambda x: x + 42)(10) == 52
        assert ffi.callback("int(int)", lambda x: x + "", -66)(10) == -66
        assert ffi.callback("int(int)", lambda x: x + "", error=-66)(10) == -66

    def test_ffi_callback_onerror(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        seen = []
        def myerror(exc, val, tb):
            seen.append(exc)
        cb = ffi.callback("int(int)", lambda x: x + "", onerror=myerror)
        assert cb(10) == 0
        cb = ffi.callback("int(int)", lambda x:int(1E100), -66, onerror=myerror)
        assert cb(10) == -66
        assert seen == [TypeError, OverflowError]

    def test_ffi_callback_decorator(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        assert ffi.callback(ffi.typeof("int(*)(int)"))(lambda x: x + 42)(10) == 52
        deco = ffi.callback("int(int)", error=-66)
        assert deco(lambda x: x + "")(10) == -66
        assert deco(lambda x: x + 42)(10) == 52

    def test_ffi_callback_onerror(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        seen = []
        def oops(*args):
            seen.append(args)

        @ffi.callback("int(int)", onerror=oops)
        def fn1(x):
            return x + ""
        assert fn1(10) == 0

        @ffi.callback("int(int)", onerror=oops, error=-66)
        def fn2(x):
            return x + ""
        assert fn2(10) == -66

        assert len(seen) == 2
        exc, val, tb = seen[0]
        assert exc is TypeError
        assert isinstance(val, TypeError)
        assert tb.tb_frame.f_code.co_name == "fn1"
        exc, val, tb = seen[1]
        assert exc is TypeError
        assert isinstance(val, TypeError)
        assert tb.tb_frame.f_code.co_name == "fn2"
        del seen[:]
        #
        raises(TypeError, ffi.callback, "int(int)",
               lambda x: x, onerror=42)   # <- not callable

    def test_ffi_getctype(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        assert ffi.getctype("int") == "int"
        assert ffi.getctype("int", 'x') == "int x"
        assert ffi.getctype("int*") == "int *"
        assert ffi.getctype("int*", '') == "int *"
        assert ffi.getctype("int*", 'x') == "int * x"
        assert ffi.getctype("int", '*') == "int *"
        assert ffi.getctype("int", replace_with=' * x ') == "int * x"
        assert ffi.getctype(ffi.typeof("int*"), '*') == "int * *"
        assert ffi.getctype("int", '[5]') == "int[5]"
        assert ffi.getctype("int[5]", '[6]') == "int[6][5]"
        assert ffi.getctype("int[5]", '(*)') == "int(*)[5]"
        # special-case for convenience: automatically put '()' around '*'
        assert ffi.getctype("int[5]", '*') == "int(*)[5]"
        assert ffi.getctype("int[5]", '*foo') == "int(*foo)[5]"
        assert ffi.getctype("int[5]", ' ** foo ') == "int(** foo)[5]"

    def test_addressof(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        a = ffi.new("int[10]")
        b = ffi.addressof(a, 5)
        b[2] = -123
        assert a[7] == -123

    def test_handle(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        x = [2, 4, 6]
        xp = ffi.new_handle(x)
        assert ffi.typeof(xp) == ffi.typeof("void *")
        assert ffi.from_handle(xp) is x
        yp = ffi.new_handle([6, 4, 2])
        assert ffi.from_handle(yp) == [6, 4, 2]

    def test_ffi_cast(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        assert ffi.cast("int(*)(int)", 0) == ffi.NULL
        ffi.callback("int(int)")      # side-effect of registering this string
        raises(ffi.error, ffi.cast, "int(int)", 0)

    def test_ffi_invalid_type(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        e = raises(ffi.error, ffi.cast, "", 0)
        assert str(e.value) == ("identifier expected\n"
                                "\n"
                                "^")
        e = raises(ffi.error, ffi.cast, "struct struct", 0)
        assert str(e.value) == ("struct or union name expected\n"
                                "struct struct\n"
                                "       ^")
        e = raises(ffi.error, ffi.cast, "struct never_heard_of_s", 0)
        assert str(e.value) == ("undefined struct/union name\n"
                                "struct never_heard_of_s\n"
                                "       ^")
        e = raises(ffi.error, ffi.cast, "\t\n\x01\x1f~\x7f\x80\xff", 0)
        assert str(e.value) == ("identifier expected\n"
                                "  ??~???\n"
                                "  ^")
        e = raises(ffi.error, ffi.cast, "X" * 600, 0)
        assert str(e.value) == ("undefined type name")

    def test_ffi_buffer(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        a = ffi.new("signed char[]", [5, 6, 7])
        assert ffi.buffer(a)[:] == '\x05\x06\x07'

    def test_ffi_from_buffer(self):
        import _cffi_backend as _cffi1_backend
        import array
        ffi = _cffi1_backend.FFI()
        a = array.array('H', [10000, 20000, 30000])
        c = ffi.from_buffer(a)
        assert ffi.typeof(c) is ffi.typeof("char[]")
        ffi.cast("unsigned short *", c)[1] += 500
        assert list(a) == [10000, 20500, 30000]

    def test_ffi_types(self):
        import _cffi_backend as _cffi1_backend
        CData = _cffi1_backend.FFI.CData
        CType = _cffi1_backend.FFI.CType
        ffi = _cffi1_backend.FFI()
        assert isinstance(ffi.cast("int", 42), CData)
        assert isinstance(ffi.typeof("int"), CType)

    def test_ffi_gc(self):
        import _cffi_backend as _cffi1_backend
        ffi = _cffi1_backend.FFI()
        p = ffi.new("int *", 123)
        seen = []
        def destructor(p1):
            assert p1 is p
            assert p1[0] == 123
            seen.append(1)
        ffi.gc(p, destructor=destructor)    # instantly forgotten
        _cffi1_backend.gcp(p, destructor=destructor)
        for i in range(5):
            if seen:
                break
            import gc
            gc.collect()
        assert seen == [1, 1]
