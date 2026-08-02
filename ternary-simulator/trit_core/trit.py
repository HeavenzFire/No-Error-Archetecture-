"""
Balanced Ternary Trit Implementation

A trit is the ternary equivalent of a bit, with three possible values:
- -1 (FALSE/NEGATIVE)
-  0 (NEUTRAL/ZERO)
- +1 (TRUE/POSITIVE)

This module provides the fundamental datatype for all balanced ternary operations.
"""

from enum import IntEnum
from typing import Union, Optional


class Trit(IntEnum):
    """
    Balanced ternary trit with values {-1, 0, +1}.
    
    Implements arithmetic, logical, and comparison operations
    native to balanced ternary logic.
    """
    
    NEG = -1  # FALSE/NEGATIVE
    ZERO = 0  # NEUTRAL/ZERO
    POS = 1   # TRUE/POSITIVE
    
    def __repr__(self) -> str:
        """Human-readable representation."""
        return self.symbol()
    
    def __str__(self) -> str:
        """String representation using symbols."""
        return self.symbol()
    
    def symbol(self) -> str:
        """Return symbolic representation: '-', '0', '+'."""
        if self == Trit.NEG:
            return '-'
        elif self == Trit.ZERO:
            return '0'
        else:
            return '+'
    
    @classmethod
    def from_int(cls, value: int) -> 'Trit':
        """
        Create a Trit from an integer.
        
        Args:
            value: Integer value (-1, 0, or 1)
            
        Returns:
            Corresponding Trit
            
        Raises:
            ValueError: If value is not in {-1, 0, 1}
        """
        if value == -1:
            return cls.NEG
        elif value == 0:
            return cls.ZERO
        elif value == 1:
            return cls.POS
        else:
            raise ValueError(f"Invalid trit value: {value}. Must be -1, 0, or 1.")
    
    @classmethod
    def from_bool(cls, value: bool) -> 'Trit':
        """
        Create a Trit from a boolean.
        
        False -> NEG (-1)
        True  -> POS (+1)
        
        Args:
            value: Boolean value
            
        Returns:
            Trit.NEG for False, Trit.POS for True
        """
        return cls.POS if value else cls.NEG
    
    def to_int(self) -> int:
        """Convert Trit to integer."""
        return int(self)
    
    def to_bool(self) -> bool:
        """
        Convert Trit to boolean.
        
        NEG (-1) -> False
        POS (+1) -> True
        ZERO (0) -> Raises ValueError (ambiguous)
        
        Raises:
            ValueError: If trit is ZERO
        """
        if self == Trit.ZERO:
            raise ValueError("Cannot convert ZERO trit to boolean")
        return bool(self.to_int())
    
    def is_negative(self) -> bool:
        """Check if trit is negative (-1)."""
        return self == Trit.NEG
    
    def is_zero(self) -> bool:
        """Check if trit is zero (0)."""
        return self == Trit.ZERO
    
    def is_positive(self) -> bool:
        """Check if trit is positive (+1)."""
        return self == Trit.POS
    
    def sign(self) -> 'Trit':
        """Return the sign of the trit (identity operation)."""
        return self
    
    def abs(self) -> 'Trit':
        """
        Return absolute value of trit.
        
        |-1| = +1
        | 0| =  0
        |+1| = +1
        """
        if self == Trit.NEG:
            return Trit.POS
        return self
    
    def neg(self) -> 'Trit':
        """
        Return negation of trit (unary minus).
        
        -(-1) = +1
        -( 0) =  0
        -(+1) = -1
        """
        return Trit(-int(self))
    
    def __neg__(self) -> 'Trit':
        """Unary negation operator."""
        return self.neg()
    
    def __invert__(self) -> 'Trit':
        """Bitwise invert (same as negation in balanced ternary)."""
        return self.neg()
    
    def __add__(self, other: Union['Trit', int]) -> int:
        """
        Add two trits. Result may be outside trit range {-2, -1, 0, 1, 2}.
        
        Returns an int to accommodate carry values.
        """
        if isinstance(other, Trit):
            return self.to_int() + other.to_int()
        elif isinstance(other, int):
            return self.to_int() + other
        return NotImplemented
    
    def __sub__(self, other: Union['Trit', int]) -> int:
        """Subtract two trits. Result may be outside trit range."""
        if isinstance(other, Trit):
            return self.to_int() - other.to_int()
        elif isinstance(other, int):
            return self.to_int() - other
        return NotImplemented
    
    def __mul__(self, other: Union['Trit', int]) -> int:
        """Multiply two trits. Result may be outside trit range."""
        if isinstance(other, Trit):
            return self.to_int() * other.to_int()
        elif isinstance(other, int):
            return self.to_int() * other
        return NotImplemented
    
    def __floordiv__(self, other: Union['Trit', int]) -> float:
        """Division (returns float, not trit)."""
        if isinstance(other, Trit):
            if other == Trit.ZERO:
                raise ZeroDivisionError("Division by zero trit")
            return self.to_int() / other.to_int()
        elif isinstance(other, int):
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            return self.to_int() / other
        return NotImplemented
    
    def min(self, other: 'Trit') -> 'Trit':
        """
        Return minimum of two trits (ternary MIN operation).
        
        Truth table:
        MIN(-1, x) = -1
        MIN( 0, x) = x if x < 0 else 0
        MIN(+1, x) = x
        """
        return Trit(min(self.to_int(), other.to_int()))
    
    def max(self, other: 'Trit') -> 'Trit':
        """
        Return maximum of two trits (ternary MAX operation).
        
        Truth table:
        MAX(-1, x) = x
        MAX( 0, x) = x if x > 0 else 0
        MAX(+1, x) = +1
        """
        return Trit(max(self.to_int(), other.to_int()))
    
    def compare(self, other: 'Trit') -> 'Trit':
        """
        Compare two trits.
        
        Returns:
            -1 if self < other
             0 if self == other
            +1 if self > other
        """
        diff = self.to_int() - other.to_int()
        if diff < 0:
            return Trit.NEG
        elif diff > 0:
            return Trit.POS
        else:
            return Trit.ZERO
    
    def __lt__(self, other: 'Trit') -> bool:
        """Less than comparison."""
        return self.to_int() < other.to_int()
    
    def __le__(self, other: 'Trit') -> bool:
        """Less than or equal comparison."""
        return self.to_int() <= other.to_int()
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if isinstance(other, Trit):
            return self.to_int() == other.to_int()
        elif isinstance(other, int):
            return self.to_int() == other
        return NotImplemented
    
    def __ne__(self, other: object) -> bool:
        """Inequality comparison."""
        return not self.__eq__(other)
    
    def __gt__(self, other: 'Trit') -> bool:
        """Greater than comparison."""
        return self.to_int() > other.to_int()
    
    def __ge__(self, other: 'Trit') -> bool:
        """Greater than or equal comparison."""
        return self.to_int() >= other.to_int()
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash(self.to_int())
    
    @staticmethod
    def truth_table(operation: str) -> dict:
        """
        Generate truth table for specified operation.
        
        Args:
            operation: One of 'NEG', 'MIN', 'MAX', 'ADD', 'SUB', 'MUL', 'COMPARE', 'ABS', 'SIGN'
            
        Returns:
            Dictionary mapping inputs to outputs
        """
        trits = [Trit.NEG, Trit.ZERO, Trit.POS]
        table = {}
        
        if operation == 'NEG':
            for t in trits:
                table[str(t)] = str(t.neg())
                
        elif operation in ['MIN', 'MAX']:
            op_func = getattr(Trit, operation.lower())
            for a in trits:
                for b in trits:
                    key = f"{a},{b}"
                    result = getattr(a, op_func.__name__)(b)
                    table[key] = str(result)
                    
        elif operation in ['ADD', 'SUB', 'MUL']:
            for a in trits:
                for b in trits:
                    key = f"{a},{b}"
                    if operation == 'ADD':
                        result = a.to_int() + b.to_int()
                    elif operation == 'SUB':
                        result = a.to_int() - b.to_int()
                    else:  # MUL
                        result = a.to_int() * b.to_int()
                    table[key] = result
                    
        elif operation == 'COMPARE':
            for a in trits:
                for b in trits:
                    key = f"{a},{b}"
                    result = a.compare(b)
                    table[key] = str(result)
                    
        elif operation == 'ABS':
            for t in trits:
                table[str(t)] = str(t.abs())
                
        elif operation == 'SIGN':
            for t in trits:
                table[str(t)] = str(t.sign())
        
        return table


# Convenience constants
NEG = Trit.NEG
ZERO = Trit.ZERO
POS = Trit.POS


def normalize_to_trit(value: int) -> tuple[list[Trit], Trit]:
    """
    Normalize an integer value to balanced ternary representation.
    
    Args:
        value: Integer value to normalize
        
    Returns:
        Tuple of (list of trits representing the value, carry trit)
        
    Example:
        normalize_to_trit(2) -> ([POS, NEG], POS)  # 2 = 3 - 1 = 1*3^1 + (-1)*3^0
    """
    if value == 0:
        return [ZERO], ZERO
    
    trits = []
    carry = ZERO
    n = abs(value)
    
    while n > 0:
        remainder = n % 3
        n = n // 3
        
        if remainder == 0:
            trits.append(ZERO)
        elif remainder == 1:
            trits.append(POS)
        else:  # remainder == 2
            trits.append(NEG)
            n += 1  # Carry to next position
    
    # Apply sign
    if value < 0:
        trits = [t.neg() for t in trits]
    
    return trits, ZERO


if __name__ == "__main__":
    # Demo usage
    print("=== Balanced Ternary Trit Demo ===\n")
    
    print("Trit values:")
    print(f"  NEG: {NEG} ({NEG.to_int()})")
    print(f"  ZERO: {ZERO} ({ZERO.to_int()})")
    print(f"  POS: {POS} ({POS.to_int()})")
    
    print("\nBasic operations:")
    a, b = POS, NEG
    print(f"  {a} + {b} = {a + b}")
    print(f"  {a} - {b} = {a - b}")
    print(f"  {a} × {b} = {a * b}")
    print(f"  -{a} = {-a}")
    print(f"  |{b}| = {b.abs()}")
    
    print("\nComparisons:")
    print(f"  {NEG} < {ZERO}: {NEG < ZERO}")
    print(f"  {ZERO} < {POS}: {ZERO < POS}")
    print(f"  {POS} > {NEG}: {POS > NEG}")
    
    print("\nTruth table for ADD:")
    table = Trit.truth_table('ADD')
    for inputs, output in table.items():
        print(f"  {inputs} -> {output}")
    
    print("\nNormalization examples:")
    for val in [-2, -1, 0, 1, 2, 3, 4, 5]:
        trits, _ = normalize_to_trit(val)
        trit_str = ''.join(str(t) for t in reversed(trits))
        print(f"  {val:3d} -> {trit_str}")
