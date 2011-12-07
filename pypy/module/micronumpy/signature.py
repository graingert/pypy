from pypy.rlib.objectmodel import r_dict, compute_identity_hash
from pypy.rlib.rarithmetic import intmask


# def components_eq(lhs, rhs):
#     if len(lhs) != len(rhs):
#         return False
#     for i in range(len(lhs)):
#         v1, v2 = lhs[i], rhs[i]
#         if type(v1) is not type(v2) or not v1.eq(v2):
#             return False
#     return True

# def components_hash(components):
#     res = 0x345678
#     for component in components:
#         res = intmask((1000003 * res) ^ component.hash())
#     return res

def sigeq(one, two):
    return one.eq(two)

def sighash(sig):
    return sig.hash()

known_sigs = r_dict(sigeq, sighash)

def find_sig(sig):
    return known_sigs.setdefault(sig, sig)

class Signature(object):
    def eq(self, other):
        return self is other

    def hash(self):
        return compute_identity_hash(self)

class ViewSignature(Signature):
    def __init__(self, child):
        self.child = child
    
    def eq(self, other):
        if type(self) != type(other):
            return False
        return self.child.eq(other.child)

    def hash(self):
        return self.child.hash() ^ 0x12345

    def debug_repr(self):
        return 'Slice(%s)' % self.child.debug_repr()

class ArraySignature(Signature):
    def debug_repr(self):
        return 'Array'

class ScalarSignature(Signature):
    def debug_repr(self):
        return 'Scalar'

class FlatiterSignature(ViewSignature):
    def debug_repr(self):
        return 'FlatIter(%s)' % self.child.debug_repr()

class Call1(Signature):
    def __init__(self, func, child):
        self.func = func
        self.child = child

    def hash(self):
        return compute_identity_hash(self.func) ^ (self.child.hash() << 1)

    def eq(self, other):
        if type(other) != type(self):
            return False
        return self.child.eq(other.child)

    def debug_repr(self):
        return 'Call1(%s, %s)' % (self.func.func_name,
                                  self.child.debug_repr())

class Call2(Signature):
    def __init__(self, func, left, right):
        self.func = func
        self.left = left
        self.right = right

    def hash(self):
        return (compute_identity_hash(self.func) ^ (self.left.hash() << 1) ^
                (self.right.hash() << 2))

    def eq(self, other):
        if type(other) != type(self):
            return False
        return self.left.eq(other.left) and self.right.eq(other.right)

    def debug_repr(self):
        return 'Call2(%s, %s, %s)' % (self.func.func_name,
                                      self.left.debug_repr(),
                                      self.right.debug_repr())

class ReduceSignature(Call1):
    pass

# class Signature(BaseSignature):
#     _known_sigs = r_dict(components_eq, components_hash)

#     _attrs_ = ["components"]
#     _immutable_fields_ = ["components[*]"]

#     def __init__(self, components):
#         self.components = components

#     @staticmethod
#     def find_sig(components):
#         return Signature._known_sigs.setdefault(components, Signature(components))

# class Call1(BaseSignature):
#     _immutable_fields_ = ["func", "name"]

#     def __init__(self, func):
#         self.func = func
#         self.name = func.func_name

# class Call2(BaseSignature):
#     _immutable_fields_ = ["func", "name"]

#     def __init__(self, func):
#         self.func = func
#         self.name = func.func_name
