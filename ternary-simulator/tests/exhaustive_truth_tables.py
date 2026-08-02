"""
Exhaustive Truth Table Validation for Balanced Ternary

Generates and validates complete truth tables for all basic operations:
- Unary operations (NEG, ABS)
- Binary arithmetic (ADD, SUB, MUL)
- Binary logic (AND, OR, XOR, etc.)
- Comparators

Outputs validation reports and verifies mathematical properties.
"""

from typing import Dict, List, Tuple, Any
from trit_core.trit import Trit, NEG, ZERO, POS
from trit_core.arithmetic import TritVector, BalancedTernaryArithmetic, generate_addition_truth_table
from trit_core.logic import TernaryLogic


class TruthTableValidator:
    """Validates balanced ternary truth tables for correctness."""
    
    def __init__(self):
        self.trits = [NEG, ZERO, POS]
        self.validation_results = {}
    
    # ==================== UNARY VALIDATION ====================
    
    def validate_negation(self) -> bool:
        """Validate NOT operation truth table."""
        expected = {
            NEG: POS,
            ZERO: ZERO,
            POS: NEG,
        }
        
        print("Validating NEGATION:")
        all_pass = True
        for input_val, expected_output in expected.items():
            actual = TernaryLogic.NOT(input_val)
            passed = actual == expected_output
            all_pass = all_pass and passed
            status = "✓" if passed else "✗"
            print(f"  {status} NOT({input_val}) = {actual} (expected {expected_output})")
        
        self.validation_results['NEGATION'] = all_pass
        return all_pass
    
    def validate_abs(self) -> bool:
        """Validate ABS operation truth table."""
        expected = {
            NEG: POS,
            ZERO: ZERO,
            POS: POS,
        }
        
        print("\nValidating ABSOLUTE VALUE:")
        all_pass = True
        for input_val, expected_output in expected.items():
            actual = Trit.abs(input_val)
            passed = actual == expected_output
            all_pass = all_pass and passed
            status = "✓" if passed else "✗"
            print(f"  {status} |{input_val}| = {actual} (expected {expected_output})")
        
        self.validation_results['ABS'] = all_pass
        return all_pass
    
    # ==================== BINARY LOGIC VALIDATION ====================
    
    def validate_and(self) -> bool:
        """Validate AND operation (MIN)."""
        print("\nValidating AND (MIN):")
        all_pass = True
        
        for a in self.trits:
            for b in self.trits:
                expected = Trit(min(a.to_int(), b.to_int()))
                actual = TernaryLogic.AND(a, b)
                passed = actual == expected
                all_pass = all_pass and passed
                status = "✓" if passed else "✗"
                if not passed:
                    print(f"  {status} AND({a}, {b}) = {actual} (expected {expected})")
        
        if all_pass:
            print(f"  ✓ All 9 cases passed")
        
        self.validation_results['AND'] = all_pass
        return all_pass
    
    def validate_or(self) -> bool:
        """Validate OR operation (MAX)."""
        print("\nValidating OR (MAX):")
        all_pass = True
        
        for a in self.trits:
            for b in self.trits:
                expected = Trit(max(a.to_int(), b.to_int()))
                actual = TernaryLogic.OR(a, b)
                passed = actual == expected
                all_pass = all_pass and passed
                status = "✓" if passed else "✗"
                if not passed:
                    print(f"  {status} OR({a}, {b}) = {actual} (expected {expected})")
        
        if all_pass:
            print(f"  ✓ All 9 cases passed")
        
        self.validation_results['OR'] = all_pass
        return all_pass
    
    def validate_xor(self) -> bool:
        """Validate XOR operation."""
        print("\nValidating XOR:")
        all_pass = True
        
        for a in self.trits:
            for b in self.trits:
                if a == ZERO or b == ZERO:
                    expected = ZERO
                elif a == b:
                    expected = NEG
                else:
                    expected = POS
                
                actual = TernaryLogic.XOR(a, b)
                passed = actual == expected
                all_pass = all_pass and passed
                status = "✓" if passed else "✗"
                if not passed:
                    print(f"  {status} XOR({a}, {b}) = {actual} (expected {expected})")
        
        if all_pass:
            print(f"  ✓ All 9 cases passed")
        
        self.validation_results['XOR'] = all_pass
        return all_pass
    
    # ==================== ARITHMETIC VALIDATION ====================
    
    def validate_single_trit_addition(self) -> bool:
        """Validate single trit addition with carry."""
        print("\nValidating Single-Trit Addition:")
        table = generate_addition_truth_table()
        
        all_pass = True
        expected_count = 27  # 3^3 combinations (a, b, carry_in)
        
        for key, (result, carry_out) in table.items():
            a_str, b_str, carry_in_str = key.split(',')
            a = Trit([NEG, ZERO, POS][['-', '0', '+'].index(a_str)])
            b = Trit([NEG, ZERO, POS][['-', '0', '+'].index(b_str)])
            carry_in = Trit([NEG, ZERO, POS][['-', '0', '+'].index(carry_in_str)])
            
            # Verify by computing expected values
            total = a.to_int() + b.to_int() + carry_in.to_int()
            
            if total <= -2:
                exp_result, exp_carry = POS, NEG
            elif total == -1:
                exp_result, exp_carry = NEG, ZERO
            elif total == 0:
                exp_result, exp_carry = ZERO, ZERO
            elif total == 1:
                exp_result, exp_carry = POS, ZERO
            else:  # total >= 2
                exp_result, exp_carry = NEG, POS
            
            passed = (result == exp_result and carry_out == exp_carry)
            all_pass = all_pass and passed
            
            if not passed:
                print(f"  ✗ {key} -> result={result}, carry={carry_out} "
                      f"(expected result={exp_result}, carry={exp_carry})")
        
        if all_pass:
            print(f"  ✓ All {expected_count} cases passed")
        
        self.validation_results['SINGLE_TRIT_ADD'] = all_pass
        return all_pass
    
    def validate_multitrit_arithmetic(self) -> bool:
        """Validate multi-trit arithmetic operations."""
        print("\nValidating Multi-Trit Arithmetic:")
        
        test_cases = [
            # (a, b, expected_sum, expected_diff, expected_prod)
            (5, 3, 8, 2, 15),
            (-5, 3, -2, -8, -15),
            (5, -3, 2, 8, -15),
            (-5, -3, -8, -2, 15),
            (0, 7, 7, -7, 0),
            (13, 13, 26, 0, 169),
            (-1, -1, -2, 0, 1),
            (1, -1, 0, 2, -1),
        ]
        
        all_pass = True
        
        for a_val, b_val, exp_sum, exp_diff, exp_prod in test_cases:
            a = TritVector(value=a_val)
            b = TritVector(value=b_val)
            
            sum_result = BalancedTernaryArithmetic.add(a, b)
            diff_result = BalancedTernaryArithmetic.subtract(a, b)
            prod_result = BalancedTernaryArithmetic.multiply(a, b)
            
            sum_ok = sum_result.to_int() == exp_sum
            diff_ok = diff_result.to_int() == exp_diff
            prod_ok = prod_result.to_int() == exp_prod
            
            case_passed = sum_ok and diff_ok and prod_ok
            all_pass = all_pass and case_passed
            
            status = "✓" if case_passed else "✗"
            if not case_passed:
                print(f"  {status} {a_val} op {b_val}:")
                if not sum_ok:
                    print(f"      ADD: got {sum_result.to_int()}, expected {exp_sum}")
                if not diff_ok:
                    print(f"      SUB: got {diff_result.to_int()}, expected {exp_diff}")
                if not prod_ok:
                    print(f"      MUL: got {prod_result.to_int()}, expected {exp_prod}")
        
        if all_pass:
            print(f"  ✓ All {len(test_cases)} test cases passed")
        
        self.validation_results['MULTITRIT_ARITH'] = all_pass
        return all_pass
    
    # ==================== PROPERTY VALIDATION ====================
    
    def validate_algebraic_properties(self) -> bool:
        """Validate fundamental algebraic properties."""
        print("\nValidating Algebraic Properties:")
        
        all_pass = True
        
        # Test commutativity of AND and OR
        for a in self.trits:
            for b in self.trits:
                if TernaryLogic.AND(a, b) != TernaryLogic.AND(b, a):
                    print(f"  ✗ AND not commutative: AND({a},{b}) ≠ AND({b},{a})")
                    all_pass = False
                if TernaryLogic.OR(a, b) != TernaryLogic.OR(b, a):
                    print(f"  ✗ OR not commutative: OR({a},{b}) ≠ OR({b},{a})")
                    all_pass = False
        
        # Test associativity of AND
        for a in self.trits:
            for b in self.trits:
                for c in self.trits:
                    left = TernaryLogic.AND(TernaryLogic.AND(a, b), c)
                    right = TernaryLogic.AND(a, TernaryLogic.AND(b, c))
                    if left != right:
                        print(f"  ✗ AND not associative")
                        all_pass = False
        
        # Test De Morgan's laws (adapted for ternary)
        for a in self.trits:
            for b in self.trits:
                # NOT(AND(a,b)) should equal OR(NOT(a), NOT(b))
                left = TernaryLogic.NOT(TernaryLogic.AND(a, b))
                right = TernaryLogic.OR(TernaryLogic.NOT(a), TernaryLogic.NOT(b))
                if left != right:
                    print(f"  ✗ De Morgan's law failed for AND: NOT(AND({a},{b})) ≠ OR(NOT({a}),NOT({b}))")
                    all_pass = False
        
        # Test additive identity
        for val in [-5, 0, 3, 7, -1]:
            v = TritVector(value=val)
            zero = TritVector(value=0)
            result = BalancedTernaryArithmetic.add(v, zero)
            if result.to_int() != val:
                print(f"  ✗ Additive identity failed: {val} + 0 = {result.to_int()} ≠ {val}")
                all_pass = False
        
        # Test multiplicative identity
        for val in [-3, 1, 4]:
            v = TritVector(value=val)
            one = TritVector(value=1)
            result = BalancedTernaryArithmetic.multiply(v, one)
            if result.to_int() != val:
                print(f"  ✗ Multiplicative identity failed: {val} × 1 = {result.to_int()} ≠ {val}")
                all_pass = False
        
        if all_pass:
            print(f"  ✓ All algebraic properties validated")
        
        self.validation_results['ALGEBRAIC_PROPS'] = all_pass
        return all_pass
    
    # ==================== COMPREHENSIVE VALIDATION ====================
    
    def run_all_validations(self) -> Dict[str, bool]:
        """Run all validation tests and return results."""
        print("=" * 60)
        print("BALANCED TERNARY TRUTH TABLE VALIDATION")
        print("=" * 60)
        
        self.validate_negation()
        self.validate_abs()
        self.validate_and()
        self.validate_or()
        self.validate_xor()
        self.validate_single_trit_addition()
        self.validate_multitrit_arithmetic()
        self.validate_algebraic_properties()
        
        # Summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for v in self.validation_results.values() if v)
        
        for test_name, passed in self.validation_results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {test_name}")
        
        print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL VALIDATIONS PASSED!")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} validation(s) failed")
        
        return self.validation_results


if __name__ == "__main__":
    validator = TruthTableValidator()
    results = validator.run_all_validations()
