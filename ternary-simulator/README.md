# Balanced Ternary Simulator

A rigorous reference implementation of balanced ternary computing systems, providing a foundation for experimental research into ternary logic, arithmetic, and computer architecture.

## Project Structure

```
ternary-simulator/
├── trit_core/              # Phase 1: Core ternary datatype & operations
│   ├── __init__.py
│   ├── trit.py             # Trit datatype {-1, 0, +1}
│   ├── arithmetic.py       # Multi-trit arithmetic engine
│   └── logic.py            # Ternary logic gates
│
├── ternary_vm/             # Phase 4: Virtual CPU
│   ├── __init__.py
│   ├── registers.py        # Register file (27 GPRs + special regs)
│   └── cpu.py              # CPU with ISA implementation
│
├── tests/                  # Phase 2: Logic verification
│   └── exhaustive_truth_tables.py
│
├── compiler/               # Phase 5: (TODO)
├── benchmarks/             # Phase 6: (TODO)
└── experiments/            # Phase 7: (TODO)
```

## Implementation Status

### ✅ Phase 1 — Reference Ternary Simulator (COMPLETE)

**Core Datatype (`trit_core/trit.py`)**
- `Trit` enum with values: `NEG=-1`, `ZERO=0`, `POS=+1`
- Symbolic representation: `-`, `0`, `+`
- Conversion methods: `from_int()`, `to_int()`, `from_bool()`, `to_bool()`
- Unary operations: `neg()`, `abs()`, `sign()`
- Comparison operators: `<`, `<=`, `==`, `!=`, `>`, `>=`
- Arithmetic operators: `+`, `-`, `*`, `/` (return int for carry handling)
- Ternary-specific: `min()`, `max()`, `compare()`
- Truth table generation for all operations

**Arithmetic Engine (`trit_core/arithmetic.py`)**
- `TritVector`: Multi-trit number representation (little-endian)
- `BalancedTernaryArithmetic` static class:
  - `add()`: Carry-propagating addition
  - `subtract()`: Via negation and addition
  - `multiply()`: Shift-and-add algorithm
  - `divide()`: Quotient and remainder
  - `compare()`, `min()`, `max()`
- Full carry normalization for balanced ternary

**Logic Operations (`trit_core/logic.py`)**
- Unary: `NOT`, `ABS`, `IDENT`, constant functions
- Binary: `AND`, `OR`, `XOR`, `NAND`, `NOR`, `XNOR`, `IMPLIES`, `IFF`
- Multi-input: `MIN`, `MAX`, `MAJORITY`, `SUM`
- Complete truth table generators

### ✅ Phase 2 — Logic Verification (COMPLETE)

**Exhaustive Testing (`tests/exhaustive_truth_tables.py`)**
- Validates all unary operations (9 cases)
- Validates all binary logic operations (81 cases each)
- Validates single-trit addition with carry (27 cases)
- Validates multi-trit arithmetic (8 test cases)
- Validates algebraic properties:
  - Commutativity of AND/OR
  - Associativity of AND
  - De Morgan's laws
  - Additive identity
  - Multiplicative identity

**Results**: All 8 validation categories pass ✓

### ✅ Phase 3 — Arithmetic Engine (COMPLETE)

Verified operations:
- Addition with proper carry propagation
- Subtraction via negation
- Multiplication using partial products
- Division with remainder
- Normalization to balanced ternary digits

Example arithmetic:
```
5 + 3 = 8      (+-- + +0 = +0-)
5 × 3 = 15     (+-- × +0 = +--0)
13 + 13 = 26   (+++ + +++ = +---)
```

### ✅ Phase 4 — Virtual CPU (COMPLETE)

**Register File (`ternary_vm/registers.py`)**
- 27 general-purpose registers (R0-R26, matching 3³)
- Special registers: PC, SP, AC, IR, FLAGS
- Configurable register width (default: 9 trits)
- Flag support: N (negative), Z (zero), P (positive)

**CPU Architecture (`ternary_vm/cpu.py`)**
- Memory: 729 locations (3⁶)
- Instruction encoding/decoding
- Fetch-decode-execute cycle

**Instruction Set Architecture (ISA)**:
```
Data Movement:
  LOAD   Rdest, addr    - Load from memory to register
  STORE  Rsrc, addr     - Store register to memory

Arithmetic:
  ADD3   Rdest, Rsrc1, Rsrc2  - Balanced ternary add
  SUB3   Rdest, Rsrc1, Rsrc2  - Balanced ternary subtract
  MUL3   Rdest, Rsrc1, Rsrc2  - Balanced ternary multiply
  NEG    Rdest, Rsrc          - Negate

Logic:
  AND3   Rdest, Rsrc1, Rsrc2  - Ternary AND
  OR3    Rdest, Rsrc1, Rsrc2  - Ternary OR
  XOR3   Rdest, Rsrc1, Rsrc2  - Ternary XOR

Comparison & Control:
  CMP    Rsrc1, Rsrc2   - Compare, set flags
  JNEG   addr           - Jump if negative
  JZERO  addr           - Jump if zero
  JPOS   addr           - Jump if positive
  JMP    addr           - Unconditional jump
  HALT                  - Stop execution
  NOP                   - No operation
```

**Execution Statistics Tracking**:
- Cycle count
- Instructions executed
- Loads/stores
- Arithmetic operations
- Jumps and branches taken

## Usage Examples

### Basic Trit Operations
```python
from trit_core.trit import Trit, NEG, ZERO, POS

a = Trit.POS      # +
b = Trit.NEG      # -
print(a + b)      # 0 (integer result)
print(a.min(b))   # - (trit result)
print(-a)         # - (negation)
```

### Multi-Trit Arithmetic
```python
from trit_core.arithmetic import TritVector, BalancedTernaryArithmetic

a = TritVector(value=5)    # +--
b = TritVector(value=3)    # +0

result = BalancedTernaryArithmetic.add(a, b)
print(f"{a} + {b} = {result}")  # +-- + +0 = +0- (8)
```

### CPU Execution
```python
from ternary_vm.cpu import TernaryCPU, Instruction, Opcode
from trit_core.arithmetic import TritVector

cpu = TernaryCPU()

# Initialize registers
cpu.registers.write('R0', TritVector(value=5))
cpu.registers.write('R1', TritVector(value=3))

# Execute ADD3
# ... instruction execution ...

result = cpu.registers.read('R2')
print(f"Result: {result.to_int()}")  # 8
```

### Truth Table Validation
```bash
cd ternary-simulator
PYTHONPATH=. python tests/exhaustive_truth_tables.py
```

Output:
```
============================================================
BALANCED TERNARY TRUTH TABLE VALIDATION
============================================================
✓ PASS: NEGATION
✓ PASS: ABS
✓ PASS: AND
✓ PASS: OR
✓ PASS: XOR
✓ PASS: SINGLE_TRIT_ADD
✓ PASS: MULTITRIT_ARITH
✓ PASS: ALGEBRAIC_PROPS

Total: 8/8 tests passed
🎉 ALL VALIDATIONS PASSED!
```

## Next Phases (TODO)

### Phase 5 — Compiler
- Parser for high-level ternary expressions
- Optimizer for ternary-specific patterns
- Code generator for VM instructions

### Phase 6 — Benchmarking
Benchmark categories:
- Matrix multiplication
- Graph traversal
- Sorting algorithms
- FFT
- Transformer inference kernels
- Sparse linear algebra

Metrics:
- Operations per second
- Memory footprint
- Instruction count
- Energy estimates (abstract cost model)
- Branch behavior

### Phase 7 — Experimental Modules
- **Phase modulation encoding**: Complex phase representations (-120°, 0°, +120°)
- **729-node attractor network**: Discrete dynamical system for memory

## Design Principles

1. **Mathematical Rigor**: All operations are precisely defined and validated
2. **Reproducibility**: Reference implementation for comparison
3. **Empirical Validation**: Claims about efficiency must be measured, not assumed
4. **Extensibility**: Modular design supports experimental additions
5. **Documentation**: Comprehensive truth tables and property verification

## References

- Balanced ternary logic gates and arithmetic circuits
- Memristive balanced ternary univariate logic (PMC)
- Memristor-based balanced ternary full adder design (Wiley)

## License

MIT License
