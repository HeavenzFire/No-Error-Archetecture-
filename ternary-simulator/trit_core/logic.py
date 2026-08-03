"""
Balanced Ternary Logic Operations

Implements ternary logic gates and operations:
- Unary: NOT (NEGATION)
- Binary: AND, OR, XOR, NAND, NOR, XNOR
- Multi-input: MIN, MAX, MAJORITY
- Implication and equivalence operators

All operations follow balanced ternary logic semantics.
"""

from typing import List, Tuple, Callable
from trit_core.trit import Trit, NEG, ZERO, POS


class TernaryLogic:
    """
    Static class providing balanced ternary logic operations.
    
    In balanced ternary logic:
    - NEG (-1) represents FALSE
    - ZERO (0) represents UNKNOWN/NEUTRAL  
    - POS (+1) represents TRUE
    """
    
    # ==================== UNARY OPERATIONS ====================
    
    @staticmethod
    def NOT(x: Trit) -> Trit:
        """
        Logical negation (NOT).
        
        NOT(-1) = +1
        NOT( 0) =  0
        NOT(+1) = -1
        """
        return x.neg()
    
    @staticmethod
    def ABS(x: Trit) -> Trit:
        """
        Absolute value.
        
        ABS(-1) = +1
        ABS( 0) =  0
        ABS(+1) = +1
        """
        return x.abs()
    
    @staticmethod
    def IDENT(x: Trit) -> Trit:
        """Identity operation (returns input unchanged)."""
        return x
    
    @staticmethod
    def ZERO_FUNC(x: Trit) -> Trit:
        """Constant zero function."""
        return ZERO
    
    @staticmethod
    def ONE_FUNC(x: Trit) -> Trit:
        """Constant positive function."""
        return POS
    
    @staticmethod
    def NEG_ONE_FUNC(x: Trit) -> Trit:
        """Constant negative function."""
        return NEG
    
    # ==================== BINARY OPERATIONS ====================
    
    @staticmethod
    def AND(a: Trit, b: Trit) -> Trit:
        """
        Logical AND (minimum).
        
        Returns the minimum of two trits.
        True only if both inputs are true.
        
        Truth table:
        AND(-1, x) = -1
        AND( 0, x) = x if x <= 0 else 0
        AND(+1, x) = x
        """
        return a.min(b)
    
    @staticmethod
    def OR(a: Trit, b: Trit) -> Trit:
        """
        Logical OR (maximum).
        
        Returns the maximum of two trits.
        False only if both inputs are false.
        
        Truth table:
        OR(-1, x) = x
        OR( 0, x) = x if x >= 0 else 0
        OR(+1, x) = +1
        """
        return a.max(b)
    
    @staticmethod
    def XOR(a: Trit, b: Trit) -> Trit:
        """
        Exclusive OR (XOR).
        
        Returns:
        - POS if inputs differ and neither is ZERO
        - NEG if inputs are same and non-zero
        - ZERO if either input is ZERO
        """
        if a == ZERO or b == ZERO:
            return ZERO
        elif a == b:
            return NEG
        else:
            return POS
    
    @staticmethod
    def NAND(a: Trit, b: Trit) -> Trit:
        """
        NOT AND (NAND).
        
        NAND(a, b) = NOT(AND(a, b))
        """
        return TernaryLogic.NOT(TernaryLogic.AND(a, b))
    
    @staticmethod
    def NOR(a: Trit, b: Trit) -> Trit:
        """
        NOT OR (NOR).
        
        NOR(a, b) = NOT(OR(a, b))
        """
        return TernaryLogic.NOT(TernaryLogic.OR(a, b))
    
    @staticmethod
    def XNOR(a: Trit, b: Trit) -> Trit:
        """
        Exclusive NOR (XNOR) / Equivalence.
        
        XNOR(a, b) = NOT(XOR(a, b))
        Returns POS if inputs are equal, NEG otherwise.
        """
        return TernaryLogic.NOT(TernaryLogic.XOR(a, b))
    
    @staticmethod
    def IMPLIES(a: Trit, b: Trit) -> Trit:
        """
        Logical implication (a → b).
        
        Equivalent to: OR(NOT(a), b)
        
        False only when a is true and b is false.
        """
        return TernaryLogic.OR(TernaryLogic.NOT(a), b)
    
    @staticmethod
    def IFF(a: Trit, b: Trit) -> Trit:
        """
        If and only if (biconditional / equivalence).
        
        IFF(a, b) = XNOR(a, b)
        """
        return TernaryLogic.XNOR(a, b)
    
    # ==================== MULTI-INPUT OPERATIONS ====================
    
    @staticmethod
    def MIN(*args: Trit) -> Trit:
        """
        Minimum of multiple trits.
        
        Returns the smallest (most negative) trit.
        """
        if not args:
            return ZERO
        result = args[0]
        for arg in args[1:]:
            result = result.min(arg)
        return result
    
    @staticmethod
    def MAX(*args: Trit) -> Trit:
        """
        Maximum of multiple trits.
        
        Returns the largest (most positive) trit.
        """
        if not args:
            return ZERO
        result = args[0]
        for arg in args[1:]:
            result = result.max(arg)
        return result
    
    @staticmethod
    def MAJORITY(*args: Trit) -> Trit:
        """
        Majority vote function.
        
        Returns the value that appears most frequently.
        Ties are resolved toward ZERO.
        """
        if not args:
            return ZERO
        
        counts = {NEG: 0, ZERO: 0, POS: 0}
        for arg in args:
            counts[arg] += 1
        
        max_count = max(counts.values())
        winners = [k for k, v in counts.items() if v == max_count]
        
        if len(winners) == 1:
            return winners[0]
        elif ZERO in winners:
            return ZERO
        else:
            # Tie between NEG and POS
            return ZERO
    
    @staticmethod
    def SUM(*args: Trit) -> Trit:
        """
        Sum of trits (with saturation).
        
        Returns saturated result clamped to {-1, 0, +1}.
        """
        if not args:
            return ZERO
        
        total = sum(arg.to_int() for arg in args)
        if total < -1:
            return NEG
        elif total > 1:
            return POS
        else:
            return Trit(total)
    
    # ==================== TRUTH TABLE GENERATORS ====================
    
    @staticmethod
    def generate_unary_table(op: Callable[[Trit], Trit]) -> dict:
        """Generate truth table for unary operation."""
        trits = [NEG, ZERO, POS]
        return {str(t): str(op(t)) for t in trits}
    
    @staticmethod
    def generate_binary_table(op: Callable[[Trit, Trit], Trit]) -> dict:
        """Generate truth table for binary operation."""
        trits = [NEG, ZERO, POS]
        table = {}
        for a in trits:
            for b in trits:
                key = f"{a},{b}"
                table[key] = str(op(a, b))
        return table
    
    @staticmethod
    def print_all_binary_tables():
        """Print truth tables for all binary operations."""
        operations = {
            'AND': TernaryLogic.AND,
            'OR': TernaryLogic.OR,
            'XOR': TernaryLogic.XOR,
            'NAND': TernaryLogic.NAND,
            'NOR': TernaryLogic.NOR,
            'XNOR': TernaryLogic.XNOR,
            'IMPLIES': TernaryLogic.IMPLIES,
            'MIN': TernaryLogic.MIN,
            'MAX': TernaryLogic.MAX,
        }
        
        for name, op in operations.items():
            print(f"\n{name} Truth Table:")
            print("A  B  |  Result")
            print("-" * 18)
            table = TernaryLogic.generate_binary_table(op)
            for inputs, output in table.items():
                a, b = inputs.split(',')
                print(f"{a:>2} {b:>3}  |  {output:>6}")


if __name__ == "__main__":
    print("=== Balanced Ternary Logic Demo ===\n")
    
    # Unary operations
    print("Unary operations:")
    print(f"  NOT({NEG}) = {TernaryLogic.NOT(NEG)}")
    print(f"  NOT({ZERO}) = {TernaryLogic.NOT(ZERO)}")
    print(f"  NOT({POS}) = {TernaryLogic.NOT(POS)}")
    
    # Binary operations
    print("\nBinary operations (sample):")
    test_pairs = [(NEG, NEG), (NEG, POS), (ZERO, POS), (POS, POS)]
    
    for a, b in test_pairs:
        print(f"\n  Inputs: {a}, {b}")
        print(f"    AND:     {TernaryLogic.AND(a, b)}")
        print(f"    OR:      {TernaryLogic.OR(a, b)}")
        print(f"    XOR:     {TernaryLogic.XOR(a, b)}")
        print(f"    NAND:    {TernaryLogic.NAND(a, b)}")
        print(f"    NOR:     {TernaryLogic.NOR(a, b)}")
        print(f"    XNOR:    {TernaryLogic.XNOR(a, b)}")
        print(f"    IMPLIES: {TernaryLogic.IMPLIES(a, b)}")
    
    # Multi-input operations
    print("\nMulti-input operations:")
    test_values = [NEG, ZERO, POS, NEG, POS]
    print(f"  Values: {test_values}")
    print(f"    MIN:      {TernaryLogic.MIN(*test_values)}")
    print(f"    MAX:      {TernaryLogic.MAX(*test_values)}")
    print(f"    MAJORITY: {TernaryLogic.MAJORITY(*test_values)}")
    
    # Complete truth tables
    print("\n" + "=" * 40)
    TernaryLogic.print_all_binary_tables()
