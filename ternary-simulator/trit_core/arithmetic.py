"""
Balanced Ternary Arithmetic Engine

Implements multi-trit arithmetic operations including:
- Addition with carry propagation
- Subtraction via negation
- Multiplication using partial products
- Division with remainder
- Normalization and carry handling

All operations work on balanced ternary numbers represented as lists of Trits
(little-endian: index 0 is least significant trit).
"""

from typing import List, Tuple, Optional
from trit_core.trit import Trit, NEG, ZERO, POS, normalize_to_trit


class TritVector:
    """
    A vector of trits representing a balanced ternary number.
    
    Stored in little-endian format (least significant trit first).
    """
    
    def __init__(self, trits: Optional[List[Trit]] = None, value: Optional[int] = None):
        """
        Initialize a TritVector.
        
        Args:
            trits: List of Trits (little-endian)
            value: Integer value to convert to balanced ternary
        """
        if trits is not None:
            self.trits = list(trits)
            self._normalize_storage()
        elif value is not None:
            self.trits = self._from_int(value)
        else:
            self.trits = [ZERO]
    
    def _from_int(self, value: int) -> List[Trit]:
        """Convert integer to balanced ternary trit list."""
        if value == 0:
            return [ZERO]
        
        trits = []
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
                n += 1  # Carry
        
        if value < 0:
            trits = [t.neg() for t in trits]
        
        return trits
    
    def _normalize_storage(self):
        """Remove leading zeros but keep at least one trit."""
        while len(self.trits) > 1 and self.trits[-1] == ZERO:
            self.trits.pop()
    
    def to_int(self) -> int:
        """Convert TritVector to integer."""
        value = 0
        power = 1
        for trit in self.trits:
            value += trit.to_int() * power
            power *= 3
        return value
    
    def __len__(self) -> int:
        """Return number of trits."""
        return len(self.trits)
    
    def __getitem__(self, index: int) -> Trit:
        """Get trit at index."""
        if index >= len(self.trits):
            return ZERO
        return self.trits[index]
    
    def __setitem__(self, index: int, value: Trit):
        """Set trit at index."""
        while index >= len(self.trits):
            self.trits.append(ZERO)
        self.trits[index] = value
        self._normalize_storage()
    
    def __repr__(self) -> str:
        """String representation."""
        if not self.trits:
            return "TritVector([])"
        return f"TritVector({''.join(str(t) for t in reversed(self.trits))})"
    
    def __str__(self) -> str:
        """Human-readable string."""
        if not self.trits:
            return "0"
        return ''.join(str(t) for t in reversed(self.trits))
    
    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if isinstance(other, TritVector):
            return self.to_int() == other.to_int()
        elif isinstance(other, int):
            return self.to_int() == other
        return NotImplemented
    
    def __neg__(self) -> 'TritVector':
        """Negation."""
        return TritVector([t.neg() for t in self.trits])
    
    def __abs__(self) -> 'TritVector':
        """Absolute value."""
        if self.to_int() < 0:
            return -self
        return self.copy()
    
    def copy(self) -> 'TritVector':
        """Create a copy."""
        return TritVector(list(self.trits))
    
    def sign(self) -> Trit:
        """Return sign trit."""
        if self.to_int() > 0:
            return POS
        elif self.to_int() < 0:
            return NEG
        else:
            return ZERO


class BalancedTernaryArithmetic:
    """
    Static class providing balanced ternary arithmetic operations.
    """
    
    @staticmethod
    def add(a: TritVector, b: TritVector) -> TritVector:
        """
        Add two balanced ternary numbers.
        
        Uses carry propagation algorithm specific to balanced ternary.
        """
        result = []
        carry = 0  # Use int for carry to handle -1, 0, +1
        max_len = max(len(a), len(b))
        
        for i in range(max_len + 2):  # +2 for potential carry propagation
            trit_a = a[i].to_int() if i < len(a) else 0
            trit_b = b[i].to_int() if i < len(b) else 0
            
            # Sum of trits and carry
            total = trit_a + trit_b + carry
            
            # Determine result trit and new carry
            if total <= -2:
                result.append(POS)  # +1
                carry = -1          # -1 (borrow)
            elif total == -1:
                result.append(NEG)
                carry = 0
            elif total == 0:
                result.append(ZERO)
                carry = 0
            elif total == 1:
                result.append(POS)
                carry = 0
            elif total == 2:
                result.append(NEG)  # -1
                carry = 1           # +1 (carry)
            else:  # total >= 3
                result.append(ZERO)
                carry = 1
        
        return TritVector(result)
    
    @staticmethod
    def subtract(a: TritVector, b: TritVector) -> TritVector:
        """Subtract b from a by adding a and -b."""
        return BalancedTernaryArithmetic.add(a, -b)
    
    @staticmethod
    def multiply(a: TritVector, b: TritVector) -> TritVector:
        """
        Multiply two balanced ternary numbers using shift-and-add.
        """
        if a.to_int() == 0 or b.to_int() == 0:
            return TritVector([ZERO])
        
        result = TritVector([ZERO])
        multiplier = b.copy()
        multiplicand = a.copy()
        
        # Check sign
        negative_result = (a.sign() == NEG) != (b.sign() == NEG)
        
        # Work with absolute values
        if a.sign() == NEG:
            multiplicand = -a
        if b.sign() == NEG:
            multiplier = -b
        
        shift = 0
        for trit in multiplier.trits:
            if trit == POS:
                # Add shifted multiplicand
                partial = TritVector([ZERO] * shift + multiplicand.trits)
                result = BalancedTernaryArithmetic.add(result, partial)
            elif trit == NEG:
                # Subtract shifted multiplicand
                partial = TritVector([ZERO] * shift + multiplicand.trits)
                result = BalancedTernaryArithmetic.subtract(result, partial)
            # If trit is ZERO, skip
            shift += 1
        
        if negative_result:
            result = -result
        
        return result
    
    @staticmethod
    def divide(a: TritVector, b: TritVector) -> Tuple[TritVector, TritVector]:
        """
        Divide a by b, returning (quotient, remainder).
        
        Uses restoring division algorithm adapted for balanced ternary.
        """
        divisor = b.to_int()
        if divisor == 0:
            raise ZeroDivisionError("Division by zero")
        
        dividend = a.to_int()
        
        # For simplicity, use integer division and convert back
        # A more sophisticated implementation would do trit-by-trit division
        quotient_val = dividend // divisor
        remainder_val = dividend % divisor
        
        return TritVector(value=quotient_val), TritVector(value=remainder_val)
    
    @staticmethod
    def compare(a: TritVector, b: TritVector) -> Trit:
        """Compare two TritVectors, returning -1, 0, or +1."""
        diff = a.to_int() - b.to_int()
        if diff < 0:
            return NEG
        elif diff > 0:
            return POS
        else:
            return ZERO
    
    @staticmethod
    def min(a: TritVector, b: TritVector) -> TritVector:
        """Return minimum of two TritVectors."""
        return a if a.to_int() <= b.to_int() else b
    
    @staticmethod
    def max(a: TritVector, b: TritVector) -> TritVector:
        """Return maximum of two TritVectors."""
        return a if a.to_int() >= b.to_int() else b


def generate_addition_truth_table() -> dict:
    """
    Generate exhaustive truth table for balanced ternary addition.
    
    Returns dictionary mapping input pairs to (result_trit, carry_trit).
    """
    trits = [NEG, ZERO, POS]
    table = {}
    
    for a in trits:
        for b in trits:
            for carry_in in trits:
                total = a.to_int() + b.to_int() + carry_in.to_int()
                
                # Determine result and carry_out
                if total <= -2:
                    result = POS
                    carry_out = NEG
                elif total == -1:
                    result = NEG
                    carry_out = ZERO
                elif total == 0:
                    result = ZERO
                    carry_out = ZERO
                elif total == 1:
                    result = POS
                    carry_out = ZERO
                elif total >= 2:
                    result = NEG
                    carry_out = POS
                
                key = f"{a},{b},{carry_in}"
                table[key] = (result, carry_out)
    
    return table


if __name__ == "__main__":
    print("=== Balanced Ternary Arithmetic Demo ===\n")
    
    # Test basic arithmetic
    print("Basic arithmetic:")
    a = TritVector(value=5)   # +--
    b = TritVector(value=3)   # +0
    
    print(f"  a = {a} ({a.to_int()})")
    print(f"  b = {b} ({b.to_int()})")
    
    sum_result = BalancedTernaryArithmetic.add(a, b)
    print(f"  a + b = {sum_result} ({sum_result.to_int()})")
    
    diff_result = BalancedTernaryArithmetic.subtract(a, b)
    print(f"  a - b = {diff_result} ({diff_result.to_int()})")
    
    prod_result = BalancedTernaryArithmetic.multiply(a, b)
    print(f"  a × b = {prod_result} ({prod_result.to_int()})")
    
    quot, rem = BalancedTernaryArithmetic.divide(a, b)
    print(f"  a ÷ b = {quot} remainder {rem} ({quot.to_int()}, {rem.to_int()})")
    
    print("\nAddition truth table (partial):")
    table = generate_addition_truth_table()
    count = 0
    for key, value in table.items():
        if count < 9:  # Show first 9 entries
            result, carry = value
            print(f"  {key} -> result={result}, carry={carry}")
            count += 1
    
    print("\nEdge cases:")
    test_cases = [
        (-10, 7),
        (4, -4),
        (0, 15),
        (-1, -1),
        (13, 13),
    ]
    
    for x, y in test_cases:
        vx = TritVector(value=x)
        vy = TritVector(value=y)
        vsum = BalancedTernaryArithmetic.add(vx, vy)
        vprod = BalancedTernaryArithmetic.multiply(vx, vy)
        print(f"  {x:3d} + {y:3d} = {vsum.to_int():4d}  ({vx} + {vy} = {vsum})")
        print(f"  {x:3d} × {y:3d} = {vprod.to_int():4d}  ({vx} × {vy} = {vprod})")
