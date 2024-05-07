import sys
from rpython.rlib.rarithmetic import ovfcheck, LONG_BIT, maxint, is_valid_int, r_uint, intmask
from rpython.rlib.objectmodel import we_are_translated
from rpython.rtyper.lltypesystem import lltype
from rpython.rtyper.lltypesystem.lloperation import llop
from rpython.jit.metainterp.resoperation import rop, ResOperation
from rpython.jit.metainterp.optimize import InvalidLoop
from rpython.jit.metainterp.optimizeopt.info import AbstractInfo, INFO_NONNULL,\
     INFO_UNKNOWN, INFO_NULL
from rpython.jit.metainterp.history import ConstInt


MAXINT = maxint
MININT = -maxint - 1

IS_64_BIT = sys.maxint > 2**32

TNUM_UNKNOWN = r_uint(0), r_uint(-1)
TNUM_KNOWN_ZERO = r_uint(0), r_uint(0)
TNUM_KNOWN_BITWISEONE = r_uint(-1), r_uint(0)
TNUM_ONLY_VALUE_DEFAULT = r_uint(0)
TNUM_ONLY_MASK_UNKNOWN = r_uint(-1)
TNUM_ONLY_MASK_DEFAULT = TNUM_ONLY_MASK_UNKNOWN


class IntBound(AbstractInfo):
    """
    Abstract domain representation of an integer,
    approximating via integer bounds and known-bits
    tri-state numbers.
    """
    _attrs_ = ('upper', 'lower', 'tvalue', 'tmask')

    def __init__(self, lower=MININT, upper=MAXINT,
                 tvalue=TNUM_ONLY_VALUE_DEFAULT,
                 tmask=TNUM_ONLY_MASK_DEFAULT,
                 do_shrinking=True):
        """
        Instantiates an abstract representation of integer.
        The default parameters set this abstract int to
        contain all integers.

        It is recommended to use the indirect constructors
        below instead of this one.
        """

        self.lower = lower
        self.upper = upper

        # known-bit analysis using tristate numbers
        assert is_valid_tnum(tvalue, tmask)
        self.tvalue = tvalue
        self.tmask = tmask         # bit=1 means unknown

        # check for unexpected overflows:
        if not we_are_translated():
            assert type(upper) is not long or is_valid_int(upper)
            assert type(lower) is not long or is_valid_int(lower)

        if do_shrinking:
            self.shrink()

        assert self._debug_check()

    @staticmethod
    def from_constant(value):
        """
        Constructs an abstract integer that represents a constant (a completely
        known integer).
        """
        # this one does NOT require a r_uint for `value`.
        assert not isinstance(value, r_uint)
        tvalue = value
        tmask = 0
        bvalue = value
        if not isinstance(value, int):
            # workaround for AddressAsInt / symbolic ints
            # by CF
            tvalue = 0
            tmask = -1
            bvalue = 0
        b = IntBound(lower=bvalue,
                     upper=bvalue,
                     tvalue=r_uint(tvalue),
                     tmask=r_uint(tmask))
        return b

    @staticmethod
    def unbounded():
        """
        Constructs an abstract integer that is completely unknown (e.g. it
        contains every integer).
        """
        return IntBound()

    @staticmethod
    def nonnegative():
        """
        Construct a non-negative abstract integer.
        """
        return IntBound(lower=0)

    @staticmethod
    def from_knownbits(tvalue, tmask, do_unmask=False):
        """
        Constructs an abstract integer where the bits determined by `tvalue`
        and `tmask` are (un-)known. tvalue and tmask must be r_uints.
        """
        assert isinstance(tvalue, r_uint) and isinstance(tmask, r_uint)
        if do_unmask:
            tvalue = unmask_zero(tvalue, tmask)
        return IntBound(tvalue=tvalue,
                        tmask=tmask)

    @staticmethod
    def _to_dec_or_hex_str_heuristics(num):
        # a few formatting heuristics
        if -1000 <= num <= 1000:
            return str(num)
        uintnum = r_uint(num)
        if uintnum & (uintnum - 1) == 0:
            # power of two, use hex
            return hex(num)
        # format number as decimal if fewer than 6 significant
        # digits, otherwise use hex
        curr = num
        exp10 = 0
        while curr % 10 == 0:
            curr //= 10
            exp10 += 1
        s = str(num)
        if len(s) - exp10 >= 6:
            return hex(num)
        return s

    def __repr__(self):
        if self.lower == MININT and self.upper == MAXINT and self.tmask == TNUM_ONLY_MASK_UNKNOWN:
            return "IntBound.unbounded()"
        if self.lower == 0 and self.upper == MAXINT and self.tmask == TNUM_ONLY_MASK_UNKNOWN:
            return "IntBound.nonnegative()"
        if self.is_constant():
            return "IntBound.from_constant(%s)" % self._to_dec_or_hex_str_heuristics(self.get_constant_int())
        # check whether the bounds imply the knownbits
        b = IntBound(self.lower, self.upper)
        s_bounds = "%s, %s" % (self._to_dec_or_hex_str_heuristics(self.lower),
                               self._to_dec_or_hex_str_heuristics(self.upper))

        if self.tmask == b.tmask and self.tvalue == b.tvalue:
            return "IntBound(%s)" % s_bounds

        # check whether the knownbits imply the bounds
        b = IntBound.from_knownbits(self.tvalue, self.tmask)
        s_tnum = "r_uint(%s), r_uint(%s)" % (bin(intmask(self.tvalue)), bin(intmask(self.tmask)))
        if self.lower == b.lower and self.upper == b.upper:
            return "IntBound.from_knownbits(%s)" % s_tnum
        return "IntBound(%s, %s)" % (s_bounds, s_tnum)

    def __str__(self):
        if self.is_constant():
            return '(%s)' % self._to_dec_or_hex_str_heuristics(self.get_constant_int())
        if self.lower == MININT:
            lower = ''
        else:
            lower = '%s <= ' % self._to_dec_or_hex_str_heuristics(self.lower)
        if self.upper == MAXINT:
            upper = ''
        else:
            upper = ' <= %s' % self._to_dec_or_hex_str_heuristics(self.upper)
        s = self.knownbits_string()
        chars = set(s)
        if chars == {'?'}:
            s = '?'
        else:
            # replace the longest sequence of same characters by ...
            prev_char = s[0]
            count = 0
            max_length = 0
            max_char = None
            for char in s:
                if char == prev_char:
                    count += 1
                else:
                    if count > max_length:
                        max_length = count
                        max_char = prev_char
                    prev_char = char
                    count = 1
            if count > max_length:
                max_length = count
                max_char = prev_char
            if max_length > 5:
                s = s.replace(max_char * max_length, max_char + '...' + max_char, 1)
            s = '0b' + s
        return '(%s%s%s)' % (lower, s, upper)

    def set_tvalue_tmask(self, tvalue, tmask):
        changed = self.tvalue != tvalue or self.tmask != tmask
        if changed:
            self.tvalue = tvalue
            self.tmask = tmask
            self.shrink()
        return changed

    def make_le(self, other):
        """
        Sets the bounds of `self` so that it only
        contains values lower than or equal to the
        values contained in `other`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        return self.make_le_const(other.upper)

    def make_le_const(self, value):
        """
        Sets the bounds of `self` so that it
        only contains values lower than or equal
        to `value`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        if value < self.upper:
            if value < self.lower:
                raise InvalidLoop
            self.upper = value
            self.shrink()
            return True
        return False

    def make_lt(self, other):
        """
        Sets the bounds of `self` so that it
        only contains values lower than the values
        contained in `other`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        return self.make_lt_const(other.upper)

    def make_lt_const(self, value):
        """
        Sets the bounds of `self` so that it
        only contains values lower than `value`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        try:
            value = ovfcheck(value - 1)
        except OverflowError:
            return False
        self.shrink()
        return self.make_le_const(value)

    def make_ge(self, other):
        """
        Sets the bounds of `self` so that it only
        contains values greater than or equal to the
        values contained in `other`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        return self.make_ge_const(other.lower)

    def make_ge_const(self, value):
        """
        Sets the bounds of `self` so that it
        only contains values greater than or equal
        to `value`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        if value > self.lower:
            if value > self.upper:
                raise InvalidLoop
            self.lower = value
            self.shrink()
            return True
        return False

    def make_gt(self, other):
        """
        Sets the bounds of `self` so that it
        only contains values greater than the values
        contained in `other`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        return self.make_gt_const(other.lower)

    def make_gt_const(self, value):
        """
        Sets the bounds of `self` so that it
        only contains values greater than `value`.
        Returns `True` iff the bound was updated.
        (Mutates `self`.)
        """
        try:
            value = ovfcheck(value + 1)
        except OverflowError:
            return False
        return self.make_ge_const(value)

    def make_eq_const(self, intval):
        """
        Sets the properties of this abstract integer
        so that it is constant and equals `intval`.
        (Mutates `self`.)
        """
        self.upper = intval
        self.lower = intval
        self.tvalue = r_uint(intval)
        self.tmask = r_uint(0)

    def make_ne_const(self, intval):
        if self.lower < intval == self.upper:
            self.upper -= 1
            self.shrink()
            return True
        if self.lower == intval < self.upper:
            self.lower += 1
            self.shrink()
            return True
        return False

    def is_constant_by_bounds(self):
        """ for internal use only! """
        return self.lower == self.upper

    def is_constant_by_knownbits(self):
        """ for internal use only! """
        return self.tmask == 0

    def is_constant(self):
        """
        Returns `True` iff this abstract integer
        does contain only one (1) concrete integer.
        """
        return self.is_constant_by_bounds() or \
               self.is_constant_by_knownbits()

    def get_constant_int(self):
        """
        Returns the only integer contained in this
        abstract integer, asserting that it
        `is_constant()`.
        """
        assert self.is_constant()
        if self.is_constant_by_bounds():
            return self.lower
        else:  # is_constant_by_knownbits
            return intmask(self.tvalue)

    def known_eq_const(self, value):
        """
        Returns `True` iff this abstract integer
        contains only one (1) integer that does
        equal `value`.
        """
        if not self.is_constant():
            return False
        if self.is_constant_by_bounds():
            return self.lower == value
        else:
            return r_uint(value) == self.tvalue

    def known_lt_const(self, value):
        """
        Returns `True` iff each number contained
        in this abstract integer is lower than
        `value`.
        """
        return self.upper < value

    def known_le_const(self, value):
        """
        Returns `True` iff each number contained
        in this abstract integer is lower than
        or equal to `value`.
        """
        return self.upper <= value

    def known_gt_const(self, value):
        """
        Returns `True` iff each number contained
        in this abstract integer is greater than
        `value`.
        """
        return self.lower > value

    def known_ge_const(self, value):
        """
        Returns `True` iff each number contained
        in this abstract integer is greater than
        equal to `value`.
        """
        return self.lower >= value

    def known_lt(self, other):
        """
        Returns `True` iff each number contained
        in this abstract integer is lower than
        each integer contained in `other`.
        """
        return self.known_lt_const(other.lower)

    def known_le(self, other):
        """
        Returns `True` iff each number contained
        in this abstract integer is lower than
        or equal to each integer contained in
        `other`.
        """
        return self.known_le_const(other.lower)

    def known_gt(self, other):
        """
        Returns `True` iff each number contained
        in this abstract integer is greater than
        each integer contained in `other`.
        """
        return other.known_lt(self)

    def known_ge(self, other):
        """
        Returns `True` iff each number contained
        in this abstract integer is greater than
        or equal to each integer contained in
        `other`.
        """
        return other.known_le(self)

    def known_ne(self, other):
        """ return True if the sets of numbers self and other must be disjoint.
        """
        if self.known_lt(other):
            return True
        if self.known_gt(other):
            return True
        both_known = self.tmask | other.tmask
        return unmask_zero(self.tvalue, both_known) != unmask_zero(other.tvalue, both_known)

    def known_nonnegative(self):
        """
        Returns `True` if this abstract integer
        only contains numbers greater than or
        equal to `0` (zero).
        """
        return 0 <= self.lower

    def known_nonnegative_by_bounds(self):
        """ for internal use only! """
        # Returns `True` if this abstract integer
        # only contains numbers greater than or
        # equal to `0` (zero).
        minest = self.get_minimum_signed()
        return 0 <= minest

    def get_minimum_signed_by_knownbits(self):
        """ for internal use only! """
        return intmask(self.tvalue | msbonly(self.tmask))

    def get_maximum_signed_by_knownbits(self):
        """ for internal use only! """
        unsigned_mask = self.tmask & ~msbonly(self.tmask)
        return intmask(self.tvalue | unsigned_mask)

    def get_minimum_signed_by_knownbits_above(self, threshold=MININT):
        """ for internal use only! """
        assert threshold <= self.upper
        min_by_knownbits = self.get_minimum_signed_by_knownbits()
        if min_by_knownbits >= threshold:
            return min_by_knownbits
        else:
            # see "Sharpening Constraint Programming
            #      approaches for Bit-Vector Theory"
            u_min_threshold = r_uint(threshold)
            #import pdb; pdb.set_trace()
            # now create our working value, the to-be minimum
            working_min = u_min_threshold # start at given minimum threshold
            working_min &= unmask_one(self.tvalue, self.tmask) # clear known 0s
            working_min |= self.tvalue # set known 1s
            # incpect changed bits
            cl2set = ~u_min_threshold & working_min
            set2cl = u_min_threshold & ~working_min
            if working_min == u_min_threshold:
                return threshold
            elif cl2set > set2cl:
                # we have set the correct bit already
                clear_mask = leading_zeros_mask(cl2set >> 1)
                working_min &= clear_mask | ~self.tmask
                return intmask(working_min)
            else:
                # flip the sign bit to handle -1 -> 0 overflow
                u_min_threshold = flip_msb(u_min_threshold)
                working_min = flip_msb(working_min)
                # we have to find the proper bit to set...
                possible_bits = ~working_min \
                                & self.tmask \
                                & leading_zeros_mask(set2cl)
                bit_to_set = lowest_set_bit_only(possible_bits)
                working_min |= bit_to_set
                # and clear all lower than that
                clear_mask = leading_zeros_mask(bit_to_set) \
                             | bit_to_set | ~self.tmask
                working_min &= clear_mask
                return intmask(flip_msb(working_min))

    def get_maximum_signed_by_knownbits_below(self, threshold=MAXINT):
        """ for internal use only! """
        max_by_knownbits = self.get_maximum_signed_by_knownbits()
        if max_by_knownbits <= self.upper:
            return max_by_knownbits
        else:
            # see "Sharpening Constraint Programming
            #      approaches for Bit-Vector Theory"
            u_max_threshold = r_uint(threshold)
            #import pdb; pdb.set_trace()
            # now create our working value, the to-be maximum
            working_max = u_max_threshold # start at given maximum threshold
            working_max &= unmask_one(self.tvalue, self.tmask) # clear known 0s
            working_max |= self.tvalue # set known 1s
            # incpect changed bits
            cl2set = ~u_max_threshold & working_max
            set2cl = u_max_threshold & ~working_max
            if working_max == u_max_threshold:
                return threshold
            elif cl2set < set2cl:
                # we have cleared the right bit already
                set_mask = next_pow2_m1(set2cl >> 1) & self.tmask
                working_max |= set_mask
                return intmask(working_max)
            else:
                # flip the sign bit to handle 1 -> 0 overflow
                u_max_threshold = flip_msb(u_max_threshold)
                working_max = flip_msb(working_max)
                # find the right bit to clear
                possible_bits = working_max \
                                & self.tmask \
                                & leading_zeros_mask(cl2set)
                bit_to_clear = lowest_set_bit_only(possible_bits)
                working_max &= ~bit_to_clear
                # and set all lower than that
                set_mask = next_pow2_m1(bit_to_clear >> 1) & self.tmask
                working_max |= set_mask
                return intmask(flip_msb(working_max))

    def get_minimum_signed(self):
        ret_b = self.lower
        return self.get_minimum_signed_by_knownbits_above(ret_b)

    def get_maximum_signed(self):
        ret_b = self.upper
        return self.get_maximum_signed_by_knownbits_below(ret_b)

    def intersect(self, other):
        """
        Mutates `self` so that it contains
        integers that are contained in `self`
        and `other`, and only those.
        Basically intersection of sets.
        Throws errors if `self` and `other`
        "disagree", meaning the result would
        contain 0 (zero) any integers.
        """
        from rpython.jit.metainterp.optimize import InvalidLoop
        if self.known_gt(other) or self.known_lt(other):
            # they don't overlap, which makes the loop invalid
            # this never happens in regular linear traces, but it can happen in
            # combination with unrolling/loop peeling
            raise InvalidLoop("two integer ranges don't overlap")

        r = self.make_ge_const(other.lower)
        r |= self.make_le_const(other.upper)

        # tnum stuff.
        union_val = self.tvalue | other.tvalue
        intersect_masks = self.tmask & other.tmask
        union_masks = self.tmask | other.tmask
        # we assert agreement, e.g. that self and other don't contradict
        unmasked_self = unmask_zero(self.tvalue, union_masks)
        unmasked_other = unmask_zero(other.tvalue, union_masks)
        assert unmasked_self == unmasked_other
        # calculate intersect value and mask
        if self.tmask != intersect_masks:
            r = self.set_tvalue_tmask(unmask_zero(union_val, intersect_masks),
                                      intersect_masks)
            assert r

        assert self._debug_check()
        return r

    def intersect_const(self, lower, upper):
        """
        Mutates `self` so that it contains
        integers that are contained in `self`
        and the range [`lower`, `upper`],
        and only those.
        Basically intersection of sets.
        Does only affect the bounds, so if
        possible the use of the `intersect`
        function is recommended instead.
        """
        r = self.make_ge_const(lower)
        if self.make_le_const(upper):
            r = True

        return r

    def add(self, value):
        return self.add_bound(IntBound.from_constant(value))

    def add_bound(self, other):
        """
        Adds the `other` abstract integer to
        `self` and returns the result.
        Must be correct in the presence of possible overflows.
        (Does not mutate `self`.)
        """

        sum_values = self.tvalue + other.tvalue
        sum_masks = self.tmask + other.tmask
        all_carries = sum_values + sum_masks
        val_carries = all_carries ^ sum_values
        tmask = self.tmask | other.tmask | val_carries
        tvalue = unmask_zero(sum_values, tmask)

        try:
            lower = ovfcheck(self.lower + other.lower)
        except OverflowError:
            return IntBound(tvalue=tvalue, tmask=tmask)
        try:
            upper = ovfcheck(self.upper + other.upper)
        except OverflowError:
            return IntBound(tvalue=tvalue, tmask=tmask)
        return IntBound(lower, upper, tvalue, tmask)

    def add_bound_cannot_overflow(self, other):
        """ returns True if self + other can never overflow """
        try:
            ovfcheck(self.upper + other.upper)
            ovfcheck(self.lower + other.lower)
        except OverflowError:
            return False
        return True

    def add_bound_no_overflow(self, other):
        """ return the bound that self + other must have, if no overflow occured,
        eg after an int_add_ovf(...), guard_no_overflow() """
        res = self.add_bound(other)

        # returning add_bound is always correct, but let's improve the range
        lower = MININT
        try:
            lower = ovfcheck(self.lower + other.lower)
        except OverflowError:
            pass
        upper = MAXINT
        try:
            upper = ovfcheck(self.upper + other.upper)
        except OverflowError:
            pass
        res.lower = lower
        res.upper = upper
        res.shrink()
        return res

    def sub_bound(self, other):
        """
        Subtracts the `other` abstract
        integer from `self` and returns the
        result.
        (Does not mutate `self`.)
        """
        res = self.add_bound(other.neg_bound())
        return res

    def sub_bound_cannot_overflow(self, other):
        try:
            ovfcheck(self.lower - other.upper)
            ovfcheck(self.upper - other.lower)
        except OverflowError:
            return False
        return True

    def sub_bound_no_overflow(self, other):
        res = self.sub_bound(other)
        # returning sub_bound is always correct, but let's improve the range
        lower = MININT
        try:
            lower = ovfcheck(self.lower - other.upper)
        except OverflowError:
            pass
        upper = MAXINT
        try:
            upper = ovfcheck(self.upper - other.lower)
        except OverflowError:
            pass
        res.lower = lower
        res.upper = upper
        res.shrink()
        return res

    def mul_bound(self, other):
        """
        Multiplies the `other` abstract
        integer with `self` and returns the
        result.
        (Does not mutate `self`.)
        """
        try:
            vals = (ovfcheck(self.upper * other.upper),
                    ovfcheck(self.upper * other.lower),
                    ovfcheck(self.lower * other.upper),
                    ovfcheck(self.lower * other.lower))
            return IntBound(min4(vals), max4(vals))
        except OverflowError:
            return IntBound.unbounded()
    mul_bound_no_overflow = mul_bound # can be improved

    def mul_bound_cannot_overflow(self, other):
        try:
            ovfcheck(self.upper * other.upper)
            ovfcheck(self.upper * other.lower)
            ovfcheck(self.lower * other.upper)
            ovfcheck(self.lower * other.lower)
        except OverflowError:
            return False
        return True

    def py_div_bound(self, other):
        """
        Divides this abstract integer by the
        `other` abstract integer and returns
        the result.
        (Does not mutate `self`.)
        """
        # we need to make sure that the 0 is not in the interval because
        # otherwise [-4, 4] / [-4, 4] would return [-1, 1], which is nonsense
        # see test_knownbits_div_bug. the first part of the check is not
        # enough, because 0 could be excluded by the known bits
        if not other.contains(0) and not (other.lower < 0 < other.upper):
            try:
                # this gives the bounds for 'int_py_div', so use the
                # Python-style handling of negative numbers and not
                # the C-style one
                vals = (ovfcheck(self.upper / other.upper),
                        ovfcheck(self.upper / other.lower),
                        ovfcheck(self.lower / other.upper),
                        ovfcheck(self.lower / other.lower))
                return IntBound(min4(vals), max4(vals))
            except OverflowError:
                pass
        return IntBound.unbounded()

    def mod_bound(self, other):
        """
        Calculates the mod of this abstract
        integer by the `other` abstract
        integer and returns the result.
        (Does not mutate `self`.)
        """
        r = IntBound.unbounded()
        if other.is_constant():
            val = other.get_constant_int()
            if val == 0:
                pass # div by 0
            elif val >= 0:        # with Python's modulo:  0 <= (x % pos) < pos
                r.make_ge_const(0)
                r.make_lt_const(val)
            else:               # with Python's modulo:  neg < (x % neg) <= 0
                r.make_gt_const(val)
                r.make_le_const(0)
        return r

    def lshift_bound(self, other):
        """
        Shifts this abstract integer `other`
        bits to the left, where `other` is
        another abstract integer.
        (Does not mutate `self`.)
        """

        tvalue, tmask = TNUM_UNKNOWN
        if other.is_constant():
            c_other = other.get_constant_int()
            if c_other >= LONG_BIT:
                 tvalue, tmask = TNUM_KNOWN_ZERO
            elif 0 <= c_other < LONG_BIT:
                tvalue = self.tvalue << r_uint(c_other)
                tmask = self.tmask << r_uint(c_other)
            # else: bits are unknown because arguments invalid

        if other.known_nonnegative() and other.known_lt_const(LONG_BIT):
            try:
                vals = (ovfcheck(self.upper << other.upper),
                        ovfcheck(self.upper << other.lower),
                        ovfcheck(self.lower << other.upper),
                        ovfcheck(self.lower << other.lower))
                return IntBound(min4(vals), max4(vals), tvalue, tmask)
            except (OverflowError, ValueError):
                pass

        return IntBound.from_knownbits(tvalue, tmask)

    def rshift_bound(self, other):
        """
        Shifts this abstract integer `other`
        bits to the right, where `other` is
        another abstract integer, and extends
        its sign.
        (Does not mutate `self`.)
        """

        # this seems to always be the signed variant..?
        tvalue, tmask = TNUM_UNKNOWN
        if other.is_constant():
            c_other = other.get_constant_int()
            if c_other >= LONG_BIT:
                # shift value out to the right, but do sign extend
                if msbonly(self.tmask): # sign-extend mask
                    tvalue, tmask = TNUM_UNKNOWN
                elif msbonly(self.tvalue): # sign-extend value
                    tvalue, tmask = TNUM_KNOWN_BITWISEONE
                else: # sign is 0 on both
                    tvalue, tmask = TNUM_KNOWN_ZERO
            elif c_other >= 0:
                # we leverage native sign extension logic
                tvalue = r_uint(intmask(self.tvalue) >> c_other)
                tmask = r_uint(intmask(self.tmask) >> c_other)
            # else: bits are unknown because arguments invalid

        lower = MININT
        upper = MAXINT
        if other.known_nonnegative() and other.known_lt_const(LONG_BIT):
            vals = (self.upper >> other.upper,
                    self.upper >> other.lower,
                    self.lower >> other.upper,
                    self.lower >> other.lower)
            lower = min4(vals)
            upper = max4(vals)
        return IntBound(lower, upper, tvalue, tmask)

    def lshift_bound_cannot_overflow(self, other):
        if other.known_nonnegative() and \
           other.known_lt_const(LONG_BIT):
            try:
                ovfcheck(self.upper << other.upper)
                ovfcheck(self.upper << other.lower)
                ovfcheck(self.lower << other.upper)
                ovfcheck(self.lower << other.lower)
                return True
            except (OverflowError, ValueError):
                pass
        return False


    def urshift_bound(self, other):
        """
        Shifts this abstract integer `other`
        bits to the right, where `other` is
        another abstract integer, *without*
        extending its sign.
        (Does not mutate `self`.)
        """

        # this seems to always be the signed variant..?
        tvalue, tmask = TNUM_UNKNOWN
        if other.is_constant():
            c_other = other.get_constant_int()
            if c_other >= LONG_BIT:
                # no sign to extend, we get constant 0
                tvalue, tmask = TNUM_KNOWN_ZERO
            elif c_other >= 0:
                tvalue = self.tvalue >> r_uint(c_other)
                tmask = self.tmask >> r_uint(c_other)
            # else: bits are unknown because arguments invalid

        # we don't do bounds on unsigned
        return IntBound.from_knownbits(tvalue, tmask)

    def and_bound(self, other):
        """
        Performs bit-wise AND of this
        abstract integer and the `other`,
        returning its result.
        (Does not mutate `self`.)
        """

        pos1 = self.known_nonnegative_by_bounds()
        pos2 = other.known_nonnegative_by_bounds()
        r = IntBound.unbounded()
        if pos1 or pos2:
            r.make_ge_const(0)
        if pos1:
            r.make_le(self)
        if pos2:
            r.make_le(other)

        res_tvalue, res_tmask = _and_tnum(self.tvalue, self.tmask, other.tvalue, other.tmask)
        r.set_tvalue_tmask(res_tvalue, res_tmask)
        return r

    def or_bound(self, other):
        """
        Performs bit-wise OR of this
        abstract integer and the `other`,
        returning its result.
        (Does not mutate `self`.)
        """

        lower = MININT
        upper = MAXINT
        if self.known_nonnegative_by_bounds() and \
                other.known_nonnegative_by_bounds():
            mostsignificant = r_uint(self.upper | other.upper)
            lower = 0
            upper = intmask(next_pow2_m1(mostsignificant))

        union_vals = self.tvalue | other.tvalue
        union_masks = self.tmask | other.tmask
        tvalue = union_vals
        tmask = union_masks & ~union_vals

        return IntBound(lower, upper, tvalue, tmask)

    def xor_bound(self, other):
        """
        Performs bit-wise XOR of this
        abstract integer and the `other`,
        returning its result.
        (Does not mutate `self`.)
        """

        lower = MININT
        upper = MAXINT
        if self.known_nonnegative_by_bounds() and \
                other.known_nonnegative_by_bounds():
            mostsignificant = r_uint(self.upper | other.upper)
            lower = 0
            upper = intmask(next_pow2_m1(mostsignificant))

        xor_vals = self.tvalue ^ other.tvalue
        union_masks = self.tmask | other.tmask
        tvalue = unmask_zero(xor_vals, union_masks)
        tmask = union_masks

        return IntBound(lower, upper, tvalue, tmask)

    def neg_bound(self):
        """
        Arithmetically negates this abstract
        integer and returns the result.
        (Does not mutate `self`.)
        """
        res = self.invert_bound()
        res = res.add(1)
        return res

    def invert_bound(self):
        """
        Performs bit-wise NOT on this
        abstract integer returning its
        result.
        (Does not mutate `self`.)
        """
        upper = ~self.lower
        lower = ~self.upper
        tvalue = unmask_zero(~self.tvalue, self.tmask)
        tmask = self.tmask
        return IntBound(lower, upper, tvalue, tmask)

    def contains(self, val):
        """
        Returns `True` iff this abstract
        integer contains the given `val`ue.
        """

        assert not isinstance(val, IntBound)

        if not we_are_translated():
            assert not isinstance(val, long)
        if not isinstance(val, int):
            if (self.lower == MININT and self.upper == MAXINT):
                return True # workaround for address as int
        if val < self.lower:
            return False
        if val > self.upper:
            return False

        u_vself = unmask_zero(self.tvalue, self.tmask)
        u_value = unmask_zero(r_uint(val), self.tmask)
        if u_vself != u_value:
            return False

        return True

    def contains_bound(self, other):
        """
        ???
        """
        assert isinstance(other, IntBound)

        # TODO: think about every caller
        assert (self.tvalue, self.tmask) == TNUM_UNKNOWN

        if not self.contains(other.lower):
            return False
        if not self.contains(other.upper):
            return False

        # not relevant at the moment
        """union_masks = self.tmask | other.tmask
        if unmask_zero(self.tvalue, self.tmask) != unmask_zero(other.tvalue, union_masks):
            return False"""

        return True

    def clone(self):
        """
        Returns an exact copy of this
        abstract integer.
        """
        res = IntBound(self.lower, self.upper,
                       self.tvalue, self.tmask)
        return res

    def make_guards(self, box, guards, optimizer):
        """
        Generates guards from the information
        we have about the numbers this
        abstract integer contains.
        """
        # TODO
        if self.is_constant():
            guards.append(ResOperation(rop.GUARD_VALUE,
                                       [box, ConstInt(self.upper)]))
            return
        if self.lower > MININT:
            bound = self.lower
            op = ResOperation(rop.INT_GE, [box, ConstInt(bound)])
            guards.append(op)
            op = ResOperation(rop.GUARD_TRUE, [op])
            guards.append(op)
        if self.upper < MAXINT:
            bound = self.upper
            op = ResOperation(rop.INT_LE, [box, ConstInt(bound)])
            guards.append(op)
            op = ResOperation(rop.GUARD_TRUE, [op])
            guards.append(op)

    def is_bool(self):
        """
        Returns `True` iff the properties
        of this abstract integer allow it to
        represent a conventional boolean
        value.
        """
        return (self.known_nonnegative() and self.known_le_const(1))

    def make_bool(self):
        """
        Mutates this abstract integer so that
        it does represent a conventional
        boolean value.
        (Mutates `self`.)
        """
        self.intersect(IntBound(0, 1))

    def getconst(self):
        """
        Returns an abstract integer that
        equals the value of this abstract
        integer if it is constant, otherwise
        throws an Exception.
        """
        if not self.is_constant():
            raise Exception("not a constant")
        return ConstInt(self.get_constant_int())

    def getnullness(self):
        """
        Returns information about whether
        this this abstract integer is known
        to be zero or not to be zero.
        """
        if self.known_gt_const(0) or \
           self.known_lt_const(0) or \
           self.tvalue != 0:
            return INFO_NONNULL
        if self.known_nonnegative() and \
           self.known_le_const(0):
            return INFO_NULL
        return INFO_UNKNOWN

    def widen(self):
        info = self.clone()
        info.widen_update()
        return info

    def widen_update(self):
        if self.lower < MININT / 2:
            self.lower = MININT
        if self.upper > MAXINT / 2:
            self.upper = MAXINT
        self.tvalue, self.tmask = TNUM_UNKNOWN


    def and_bound_backwards(self, other, result_int):
        """
        result_int == int_and(self, other)
        We want to refine our knowledge about self
        using this information

        regular &:
                  other
         &  0   1   ?
         0  0   0   0
         1  0   1   ?
         ?  0   ?   ?   <- result
        self

        backwards & (this one):
                  other
            0   1   ?
         0  ?   0   ?
         1  X?  1   ?
         ?  ?   ?   ?   <- self
        result

        If the knownbits of self and result are inconsistent,
        the values of result are used (this must not happen
        in practice and will be caught by an assert in intersect())
        """

        tvalue, tmask = _and_tnum_backwards(
            self.tvalue, self.tmask, other.tvalue, other.tmask,
            r_uint(result_int)
        )
        return IntBound.from_knownbits(tvalue, tmask)

    def or_bound_backwards(self, other, result_int):
        """
        result_int == int_or(self, other)
        We want to refine our knowledge about self
        using this information

        regular |:
                  other
         &  0   1   ?
         0  0   1   ?
         1  1   1   ?
         ?  ?   ?   ?   <- result
        self

        backwards | (this one):
                  other
            0   1   ?
         0  0   X?  X0
         1  1   ?   ?
         ?  ?   ?   ?   <- self (where X=invalid)
        result

        For every X just go ?.
        If the knownbits of self and result are inconsistent,
        the values of result are used (this must not happen
        in practice and will be caught by an assert in intersect())
        """
        pass

    def urshift_bound_backwards(self, other, result):
        """
        Performs a `urshift`/`rshift` backwards on
        `result`. Basically left-shifts
        `result` by `other` binary digits,
        filling the lower part with ?, and
        returns the result.
        """
        if not other.is_constant():
            return IntBound.unbounded()
        c_other = other.get_constant_int()
        tvalue, tmask = TNUM_UNKNOWN
        if 0 <= c_other < LONG_BIT:
            tvalue = result.tvalue << r_uint(c_other)
            tmask = result.tmask << r_uint(c_other)
            # shift ? in from the right,
            # but we know some bits from `self`
            s_tmask = (r_uint(1) << r_uint(c_other)) - 1
            s_tvalue = s_tmask & self.tvalue
            s_tmask &= self.tmask
            tvalue |= s_tvalue
            tmask |= s_tmask
        # ignore bounds # TODO: bounds
        return IntBound.from_knownbits(tvalue, tmask)
    rshift_bound_backwards = urshift_bound_backwards

    def lshift_bound_backwards(self, other, result):
        if not other.is_constant():
            return IntBound.unbounded()
        c_other = other.get_constant_int()
        tvalue, tmask = TNUM_UNKNOWN
        if 0 <= c_other < LONG_BIT:
            tvalue = result.tvalue >> r_uint(c_other)
            tmask = result.tmask >> r_uint(c_other)
            # shift ? in from the left,
            # but we know some bits from `self`
            s_tmask = leading_zeros_mask(r_uint(MININT) >> r_uint(c_other))
            s_tvalue = s_tmask & self.tvalue
            s_tmask &= self.tmask
            tvalue |= s_tvalue
            tmask |= s_tmask
        # ignore bounds # TODO: bounds
        return IntBound.from_knownbits(tvalue, tmask)

    def shrink(self):
        # some passes of bounds-knownbits synchronization
        for i in range(4):
            changed = self._shrink_bounds_by_knownbits()
            changed |= self._shrink_knownbits_by_bounds()
            if not changed:
                return

    def _shrink_bounds_by_knownbits(self):
        """
        Shrinks the bounds by the known bits.
        """
        # lower bound
        min_by_knownbits = self.get_minimum_signed_by_knownbits_above(self.lower)
        max_by_knownbits = self.get_maximum_signed_by_knownbits_below(self.upper)
        changed = self.lower != min_by_knownbits or self.upper != max_by_knownbits
        self.lower = min_by_knownbits
        # and same for upper bound
        self.upper = max_by_knownbits
        return changed

    def _shrink_knownbits_by_bounds(self):
        """
        Infers known bits from the bounds.
        Basically fills a common prefix
        from lower and upper bound into
        the knownbits.
        """

        # are we working on negative or positive values?
        # get the working values
        if (self.lower >= 0) != (self.upper >= 0):
            # nothing to do if signs are different
            # this should actually not be necessary,
            # but remains as a safe guard
            return False
        # calculate higher bit mask by bounds
        work_lower = r_uint(self.lower)
        work_upper = r_uint(self.upper)
        hbm_bounds = leading_zeros_mask(work_lower ^ work_upper)
        bounds_common = work_lower & hbm_bounds
        # we should assert agreement between bounds and knownbits here!
        assert unmask_zero(bounds_common, self.tmask) == (self.tvalue & hbm_bounds)
        hbm = hbm_bounds & self.tmask
        # apply the higher bit mask to the knownbits
        tmask = self.tmask & ~hbm
        tvalue = (bounds_common & hbm) | (self.tvalue & ~hbm)
        changed = self.tvalue != tvalue or self.tmask != tmask
        self.tmask = tmask
        self.tvalue = tvalue
        return changed

    def _debug_check(self):
        """
        Very simple debug check.
        Returns `True` iff the span of
        knownbits and the span of the bounds
        have a non-empty intersection.
        That does not guarantee for the
        actual concrete value set to contain
        any values!
        """
        min_knownbits = self.get_minimum_signed_by_knownbits()
        max_knownbits = self.get_maximum_signed_by_knownbits()
        if not min_knownbits <= self.upper:
            return False
        if not max_knownbits >= self.lower:
            return False
        # just to make sure
        if not min_knownbits <= max_knownbits:
            return False
        # make sure the set is not empty
        if self.is_constant():
            # does one constraint exclude the constant value?
            val = self.get_constant_int()
            if min_knownbits > val or max_knownbits < val \
               or self.lower > val or self.upper < val:
                return False
        else:
            # we have no constant, so keep checking
            u_lower = r_uint(self.lower)
            u_upper = r_uint(self.upper)
            # check if bounds common prefix agrees with known-bits  
            hbm_bounds = leading_zeros_mask(u_lower ^ u_upper)
            bounds_common_prefix = u_lower & hbm_bounds
            if unmask_zero(bounds_common_prefix, self.tmask) != self.tvalue & hbm_bounds:
                return False
            # for the rest of the bunch, check by minima/maxima with threshold.
            #   (side note: the whole check can be reduced to this, but for the
            #    sake of robustness we want to keep the other checks above.)
            if self.get_minimum_signed_by_knownbits_above(self.lower) > self.upper \
               or self.get_maximum_signed_by_knownbits_below(self.upper) < self.lower:
                return False
        return True

    def knownbits_string(self, unk_sym='?'):
        """
        Returns a string representation about the knownbits part of this
        abstract integer. You can give any symbol or string for the "unknown
        bits" (default: '?'), the other digits are written as '1' and '0'.
        """
        results = []
        for bit in range(LONG_BIT):
            if self.tmask & (1 << bit):
                results.append(unk_sym)
            else:
                results.append(str((self.tvalue >> bit) & 1))
        results.reverse()
        return "".join(results)


def flip_msb(val_uint):
    return val_uint ^ r_uint(MININT)

def is_valid_tnum(tvalue, tmask):
    """
    Returns `True` iff `tvalue` and `tmask`
    would be valid tri-state number fields
    of an abstract integer, meeting all
    conventions and requirements.
    """
    if not isinstance(tvalue, r_uint):
        return False
    if not isinstance(tmask, r_uint):
        return False
    return 0 == (r_uint(tvalue) & r_uint(tmask))

def leading_zeros_mask(n):
    """
    calculates a bitmask in which only the leading zeros
    of `n` are set (1).
    """
    assert isinstance(n, r_uint)
    if n == MAXINT:
        return r_uint(0)
    elif n == 0:
        return r_uint(-1)
    else:
        return ~next_pow2_m1(n)

def lowest_set_bit_only(val_uint):
    """
    Returns an val_int, but with all bits
    deleted but the lowest one that was set.
    """
    #assert isinstance(val_uint, r_uint)
    working_val = ~val_uint
    increased_val = working_val + 1
    result = (working_val^increased_val) & ~working_val
    return result

def min4(t):
    """
    Returns the minimum of the values in
    the quadruplet t.
    """
    return min(min(t[0], t[1]), min(t[2], t[3]))

def max4(t):
    """
    Returns the maximum of the values in
    the quadruplet t.
    """
    return max(max(t[0], t[1]), max(t[2], t[3]))

def msbonly(v):
    """
    Returns `v` with all bits except the
    most significant bit set to 0 (zero).
    """
    return v & (1 << (LONG_BIT-1))

def next_pow2_m1(n):
    """Calculate next power of 2 minus one, greater than n"""
    assert isinstance(n, r_uint)
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    if IS_64_BIT:
        n |= n >> 32
    return n

def unmask_one(value, mask):
    """
    Sets all unknowns determined by
    `mask` in `value` bit-wise to 1 (one)
    and returns the result.
    """
    return value | mask

def unmask_zero(value, mask):
    """
    Sets all unknowns determined by
    `mask` in `value` bit-wise to 0 (zero)
    and returns the result.
    """
    return value & ~mask


def _and_tnum(self_tvalue, self_tmask, other_tvalue, other_tmask):
    self_pmask = self_tvalue | self_tmask
    other_pmask = other_tvalue | other_tmask
    and_vals = self_tvalue & other_tvalue
    return and_vals, self_pmask & other_pmask & ~and_vals

def _and_tnum_backwards(self_tvalue, self_tmask, other_tvalue, other_tmask, result_uint):
    tvalue = self_tvalue
    tmask = self_tmask
    tvalue &= ~other_tvalue | other_tmask
    tvalue |= result_uint & other_tvalue
    tmask &= ~other_tvalue | other_tmask
    return tvalue, tmask
