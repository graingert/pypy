
/*
   DO NOT EDIT THIS FILE!

   This file is automatically generated by tools/autogen.py from tools/public_api.h.
   Run this to regenerate:
       make autogen

*/

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Long_FromLong)(HPyContext ctx, long value)
{
    return _py2h(PyLong_FromLong(value));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Long_FromUnsignedLong)(HPyContext ctx, unsigned long value)
{
    return _py2h(PyLong_FromUnsignedLong(value));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Long_FromLongLong)(HPyContext ctx, long long v)
{
    return _py2h(PyLong_FromLongLong(v));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Long_FromUnsignedLongLong)(HPyContext ctx, unsigned long long v)
{
    return _py2h(PyLong_FromUnsignedLongLong(v));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Long_FromSize_t)(HPyContext ctx, size_t value)
{
    return _py2h(PyLong_FromSize_t(value));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Long_FromSsize_t)(HPyContext ctx, HPy_ssize_t value)
{
    return _py2h(PyLong_FromSsize_t(value));
}

HPyAPI_STORAGE long _HPy_IMPL_NAME(Long_AsLong)(HPyContext ctx, HPy h)
{
    return PyLong_AsLong(_h2py(h));
}

HPyAPI_STORAGE unsigned long _HPy_IMPL_NAME(Long_AsUnsignedLong)(HPyContext ctx, HPy h)
{
    return PyLong_AsUnsignedLong(_h2py(h));
}

HPyAPI_STORAGE unsigned long _HPy_IMPL_NAME(Long_AsUnsignedLongMask)(HPyContext ctx, HPy h)
{
    return PyLong_AsUnsignedLongMask(_h2py(h));
}

HPyAPI_STORAGE long long _HPy_IMPL_NAME(Long_AsLongLong)(HPyContext ctx, HPy h)
{
    return PyLong_AsLongLong(_h2py(h));
}

HPyAPI_STORAGE unsigned long long _HPy_IMPL_NAME(Long_AsUnsignedLongLong)(HPyContext ctx, HPy h)
{
    return PyLong_AsUnsignedLongLong(_h2py(h));
}

HPyAPI_STORAGE unsigned long long _HPy_IMPL_NAME(Long_AsUnsignedLongLongMask)(HPyContext ctx, HPy h)
{
    return PyLong_AsUnsignedLongLongMask(_h2py(h));
}

HPyAPI_STORAGE size_t _HPy_IMPL_NAME(Long_AsSize_t)(HPyContext ctx, HPy h)
{
    return PyLong_AsSize_t(_h2py(h));
}

HPyAPI_STORAGE HPy_ssize_t _HPy_IMPL_NAME(Long_AsSsize_t)(HPyContext ctx, HPy h)
{
    return PyLong_AsSsize_t(_h2py(h));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Float_FromDouble)(HPyContext ctx, double v)
{
    return _py2h(PyFloat_FromDouble(v));
}

HPyAPI_STORAGE double _HPy_IMPL_NAME(Float_AsDouble)(HPyContext ctx, HPy h)
{
    return PyFloat_AsDouble(_h2py(h));
}

HPyAPI_STORAGE HPy_ssize_t _HPy_IMPL_NAME_NOPREFIX(Length)(HPyContext ctx, HPy h)
{
    return PyObject_Length(_h2py(h));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME(Number_Check)(HPyContext ctx, HPy h)
{
    return PyNumber_Check(_h2py(h));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Add)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_Add(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Subtract)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_Subtract(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Multiply)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_Multiply(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(MatrixMultiply)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_MatrixMultiply(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(FloorDivide)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_FloorDivide(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(TrueDivide)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_TrueDivide(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Remainder)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_Remainder(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Divmod)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_Divmod(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Power)(HPyContext ctx, HPy h1, HPy h2, HPy h3)
{
    return _py2h(PyNumber_Power(_h2py(h1), _h2py(h2), _h2py(h3)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Negative)(HPyContext ctx, HPy h1)
{
    return _py2h(PyNumber_Negative(_h2py(h1)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Positive)(HPyContext ctx, HPy h1)
{
    return _py2h(PyNumber_Positive(_h2py(h1)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Absolute)(HPyContext ctx, HPy h1)
{
    return _py2h(PyNumber_Absolute(_h2py(h1)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Invert)(HPyContext ctx, HPy h1)
{
    return _py2h(PyNumber_Invert(_h2py(h1)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Lshift)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_Lshift(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Rshift)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_Rshift(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(And)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_And(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Xor)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_Xor(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Or)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_Or(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Index)(HPyContext ctx, HPy h1)
{
    return _py2h(PyNumber_Index(_h2py(h1)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Long)(HPyContext ctx, HPy h1)
{
    return _py2h(PyNumber_Long(_h2py(h1)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Float)(HPyContext ctx, HPy h1)
{
    return _py2h(PyNumber_Float(_h2py(h1)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceAdd)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceAdd(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceSubtract)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceSubtract(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceMultiply)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceMultiply(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceMatrixMultiply)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceMatrixMultiply(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceFloorDivide)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceFloorDivide(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceTrueDivide)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceTrueDivide(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceRemainder)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceRemainder(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlacePower)(HPyContext ctx, HPy h1, HPy h2, HPy h3)
{
    return _py2h(PyNumber_InPlacePower(_h2py(h1), _h2py(h2), _h2py(h3)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceLshift)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceLshift(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceRshift)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceRshift(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceAnd)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceAnd(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceXor)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceXor(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(InPlaceOr)(HPyContext ctx, HPy h1, HPy h2)
{
    return _py2h(PyNumber_InPlaceOr(_h2py(h1), _h2py(h2)));
}

HPyAPI_STORAGE void _HPy_IMPL_NAME(Err_SetString)(HPyContext ctx, HPy h_type, const char *message)
{
    PyErr_SetString(_h2py(h_type), message);
}

HPyAPI_STORAGE void _HPy_IMPL_NAME(Err_SetObject)(HPyContext ctx, HPy h_type, HPy h_value)
{
    PyErr_SetObject(_h2py(h_type), _h2py(h_value));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Err_NoMemory)(HPyContext ctx)
{
    return _py2h(PyErr_NoMemory());
}

HPyAPI_STORAGE void _HPy_IMPL_NAME(Err_Clear)(HPyContext ctx)
{
    PyErr_Clear();
}

HPyAPI_STORAGE int _HPy_IMPL_NAME_NOPREFIX(IsTrue)(HPyContext ctx, HPy h)
{
    return PyObject_IsTrue(_h2py(h));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(GetAttr)(HPyContext ctx, HPy obj, HPy name)
{
    return _py2h(PyObject_GetAttr(_h2py(obj), _h2py(name)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(GetAttr_s)(HPyContext ctx, HPy obj, const char *name)
{
    return _py2h(PyObject_GetAttrString(_h2py(obj), name));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME_NOPREFIX(HasAttr)(HPyContext ctx, HPy obj, HPy name)
{
    return PyObject_HasAttr(_h2py(obj), _h2py(name));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME_NOPREFIX(HasAttr_s)(HPyContext ctx, HPy obj, const char *name)
{
    return PyObject_HasAttrString(_h2py(obj), name);
}

HPyAPI_STORAGE int _HPy_IMPL_NAME_NOPREFIX(SetAttr)(HPyContext ctx, HPy obj, HPy name, HPy value)
{
    return PyObject_SetAttr(_h2py(obj), _h2py(name), _h2py(value));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME_NOPREFIX(SetAttr_s)(HPyContext ctx, HPy obj, const char *name, HPy value)
{
    return PyObject_SetAttrString(_h2py(obj), name, _h2py(value));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(GetItem)(HPyContext ctx, HPy obj, HPy key)
{
    return _py2h(PyObject_GetItem(_h2py(obj), _h2py(key)));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME_NOPREFIX(SetItem)(HPyContext ctx, HPy obj, HPy key, HPy value)
{
    return PyObject_SetItem(_h2py(obj), _h2py(key), _h2py(value));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Repr)(HPyContext ctx, HPy obj)
{
    return _py2h(PyObject_Repr(_h2py(obj)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Str)(HPyContext ctx, HPy obj)
{
    return _py2h(PyObject_Str(_h2py(obj)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(ASCII)(HPyContext ctx, HPy obj)
{
    return _py2h(PyObject_ASCII(_h2py(obj)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(Bytes)(HPyContext ctx, HPy obj)
{
    return _py2h(PyObject_Bytes(_h2py(obj)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME_NOPREFIX(RichCompare)(HPyContext ctx, HPy v, HPy w, int op)
{
    return _py2h(PyObject_RichCompare(_h2py(v), _h2py(w), op));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME_NOPREFIX(RichCompareBool)(HPyContext ctx, HPy v, HPy w, int op)
{
    return PyObject_RichCompareBool(_h2py(v), _h2py(w), op);
}

HPyAPI_STORAGE HPy_hash_t _HPy_IMPL_NAME_NOPREFIX(Hash)(HPyContext ctx, HPy obj)
{
    return PyObject_Hash(_h2py(obj));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME(Bytes_Check)(HPyContext ctx, HPy h)
{
    return PyBytes_Check(_h2py(h));
}

HPyAPI_STORAGE HPy_ssize_t _HPy_IMPL_NAME(Bytes_Size)(HPyContext ctx, HPy h)
{
    return PyBytes_Size(_h2py(h));
}

HPyAPI_STORAGE HPy_ssize_t _HPy_IMPL_NAME(Bytes_GET_SIZE)(HPyContext ctx, HPy h)
{
    return PyBytes_GET_SIZE(_h2py(h));
}

HPyAPI_STORAGE char *_HPy_IMPL_NAME(Bytes_AsString)(HPyContext ctx, HPy h)
{
    return PyBytes_AsString(_h2py(h));
}

HPyAPI_STORAGE char *_HPy_IMPL_NAME(Bytes_AS_STRING)(HPyContext ctx, HPy h)
{
    return PyBytes_AS_STRING(_h2py(h));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Bytes_FromString)(HPyContext ctx, const char *v)
{
    return _py2h(PyBytes_FromString(v));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Bytes_FromStringAndSize)(HPyContext ctx, const char *v, HPy_ssize_t len)
{
    return _py2h(PyBytes_FromStringAndSize(v, len));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Unicode_FromString)(HPyContext ctx, const char *utf8)
{
    return _py2h(PyUnicode_FromString(utf8));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME(Unicode_Check)(HPyContext ctx, HPy h)
{
    return PyUnicode_Check(_h2py(h));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Unicode_AsUTF8String)(HPyContext ctx, HPy h)
{
    return _py2h(PyUnicode_AsUTF8String(_h2py(h)));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Unicode_FromWideChar)(HPyContext ctx, const wchar_t *w, HPy_ssize_t size)
{
    return _py2h(PyUnicode_FromWideChar(w, size));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME(List_Check)(HPyContext ctx, HPy h)
{
    return PyList_Check(_h2py(h));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(List_New)(HPyContext ctx, HPy_ssize_t len)
{
    return _py2h(PyList_New(len));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME(List_Append)(HPyContext ctx, HPy h_list, HPy h_item)
{
    return PyList_Append(_h2py(h_list), _h2py(h_item));
}

HPyAPI_STORAGE int _HPy_IMPL_NAME(Dict_Check)(HPyContext ctx, HPy h)
{
    return PyDict_Check(_h2py(h));
}

HPyAPI_STORAGE HPy _HPy_IMPL_NAME(Dict_New)(HPyContext ctx)
{
    return _py2h(PyDict_New());
}
