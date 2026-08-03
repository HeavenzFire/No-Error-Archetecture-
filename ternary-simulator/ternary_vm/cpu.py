"""
Balanced Ternary Virtual CPU

Implements a minimal balanced ternary instruction set architecture (ISA):
- LOAD/STORE operations
- Arithmetic: ADD3, SUB3, NEG
- Comparison: CMP
- Conditional jumps: JNEG, JZERO, JPOS
- Control: HALT, NOP

Memory model uses trit-addressable locations with TritVector values.
"""

from typing import Dict, List, Optional, Tuple, Callable
from enum import IntEnum
from trit_core.trit import Trit, NEG, ZERO, POS
from trit_core.arithmetic import TritVector, BalancedTernaryArithmetic
from trit_core.logic import TernaryLogic
from ternary_vm.registers import RegisterFile


class Opcode(IntEnum):
    """Instruction opcodes for the balanced ternary CPU."""
    NOP = 0       # No operation
    HALT = 1      # Stop execution
    LOAD = 2      # Load from memory to register
    STORE = 3     # Store from register to memory
    ADD3 = 4      # Balanced ternary add
    SUB3 = 5      # Balanced ternary subtract
    MUL3 = 6      # Balanced ternary multiply
    NEG = 7       # Negate register value
    CMP = 8       # Compare two registers
    JNEG = 9      # Jump if negative
    JZERO = 10    # Jump if zero
    JPOS = 11     # Jump if positive
    JMP = 12      # Unconditional jump
    AND3 = 13     # Ternary AND
    OR3 = 14      # Ternary OR
    XOR3 = 15     # Ternary XOR


class Instruction:
    """
    Represents a single balanced ternary instruction.
    
    Format: OPCODE, ARG1, ARG2, ARG3
    - OPCODE: Operation to perform
    - ARG1, ARG2, ARG3: Operands (register IDs, memory addresses, or immediate values)
    """
    
    def __init__(self, opcode: Opcode, arg1: int = 0, arg2: int = 0, arg3: int = 0):
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
    
    def __repr__(self) -> str:
        return f"Instruction({self.opcode.name}, {self.arg1}, {self.arg2}, {self.arg3})"


class Memory:
    """
    Balanced ternary memory system.
    
    Addresses are integers, values are TritVectors.
    """
    
    def __init__(self, size: int = 729):  # 3^6 = 729 memory locations
        self.size = size
        self.cells: Dict[int, TritVector] = {}
        
        # Initialize all cells to zero
        for i in range(size):
            self.cells[i] = TritVector(value=0)
    
    def read(self, address: int) -> Optional[TritVector]:
        """Read from memory address."""
        if 0 <= address < self.size:
            return self.cells[address].copy()
        return None
    
    def write(self, address: int, value: TritVector) -> bool:
        """Write to memory address."""
        if 0 <= address < self.size:
            self.cells[address] = value.copy()
            return True
        return False
    
    def load_program(self, instructions: List[Instruction], start_addr: int = 0):
        """Load a program into memory starting at given address."""
        for i, instr in enumerate(instructions):
            # Encode instruction as integer for storage
            encoded = self._encode_instruction(instr)
            self.write(start_addr + i, TritVector(value=encoded))
    
    def _encode_instruction(self, instr: Instruction) -> int:
        """Encode instruction as single integer."""
        # Simple encoding: opcode * 10000 + arg1 * 100 + arg2 * 10 + arg3
        return (int(instr.opcode) * 10000 + 
                instr.arg1 * 100 + 
                instr.arg2 * 10 + 
                instr.arg3)
    
    def _decode_instruction(self, value: int) -> Instruction:
        """Decode integer back to instruction."""
        opcode = Opcode(value // 10000)
        arg1 = (value // 100) % 100
        arg2 = (value // 10) % 10
        arg3 = value % 10
        return Instruction(opcode, arg1, arg2, arg3)
    
    def fetch_instruction(self, address: int) -> Optional[Instruction]:
        """Fetch and decode instruction from memory."""
        value = self.read(address)
        if value is None:
            return None
        return self._decode_instruction(value.to_int())


class TernaryCPU:
    """
    Balanced Ternary Virtual CPU.
    
    Executes balanced ternary instructions using a register file and memory.
    """
    
    def __init__(self, num_registers: int = 27, memory_size: int = 729):
        self.registers = RegisterFile(num_registers=num_registers)
        self.memory = Memory(size=memory_size)
        self.halted = False
        self.cycle_count = 0
        self.instructions_executed = 0
        
        # Statistics
        self.stats = {
            'loads': 0,
            'stores': 0,
            'arith_ops': 0,
            'jumps': 0,
            'branches_taken': 0,
        }
    
    def reset(self):
        """Reset CPU state."""
        self.registers.reset()
        self.halted = False
        self.cycle_count = 0
        self.instructions_executed = 0
        self.stats = {k: 0 for k in self.stats.keys()}
    
    def step(self) -> bool:
        """
        Execute one instruction cycle.
        
        Returns:
            True if execution should continue, False if halted
        """
        if self.halted:
            return False
        
        self.cycle_count += 1
        
        # Fetch
        pc_val = self.registers.read('PC')
        if pc_val is None:
            self.halted = True
            return False
        
        pc = pc_val.to_int()
        instruction = self.memory.fetch_instruction(pc)
        
        if instruction is None:
            self.halted = True
            return False
        
        # Increment PC before execute (simplified)
        self.registers.increment_pc()
        
        # Execute
        self._execute(instruction)
        self.instructions_executed += 1
        
        return not self.halted
    
    def run(self, max_cycles: int = 10000) -> bool:
        """
        Run until halted or max cycles reached.
        
        Args:
            max_cycles: Maximum number of cycles to execute
            
        Returns:
            True if completed normally, False if max cycles reached
        """
        cycles = 0
        while not self.halted and cycles < max_cycles:
            self.step()
            cycles += 1
        
        return not self.halted
    
    def _execute(self, instr: Instruction):
        """Execute a single instruction."""
        opcode = instr.opcode
        
        if opcode == Opcode.NOP:
            pass
        
        elif opcode == Opcode.HALT:
            self.halted = True
        
        elif opcode == Opcode.LOAD:
            # LOAD Rdest, addr - Load from memory to register
            reg_name = f"R{instr.arg1}"
            addr = instr.arg2
            value = self.memory.read(addr)
            if value:
                self.registers.write(reg_name, value)
                self.stats['loads'] += 1
        
        elif opcode == Opcode.STORE:
            # STORE Rsrc, addr - Store register to memory
            reg_name = f"R{instr.arg1}"
            addr = instr.arg2
            value = self.registers.read(reg_name)
            if value:
                self.memory.write(addr, value)
                self.stats['stores'] += 1
        
        elif opcode == Opcode.ADD3:
            # ADD3 Rdest, Rsrc1, Rsrc2 - Balanced ternary add
            dest = f"R{instr.arg1}"
            src1 = f"R{instr.arg2}"
            src2 = f"R{instr.arg3}"
            
            v1 = self.registers.read(src1)
            v2 = self.registers.read(src2)
            if v1 and v2:
                result = BalancedTernaryArithmetic.add(v1, v2)
                self.registers.write(dest, result)
                self._update_flags(result)
                self.stats['arith_ops'] += 1
        
        elif opcode == Opcode.SUB3:
            # SUB3 Rdest, Rsrc1, Rsrc2 - Balanced ternary subtract
            dest = f"R{instr.arg1}"
            src1 = f"R{instr.arg2}"
            src2 = f"R{instr.arg3}"
            
            v1 = self.registers.read(src1)
            v2 = self.registers.read(src2)
            if v1 and v2:
                result = BalancedTernaryArithmetic.subtract(v1, v2)
                self.registers.write(dest, result)
                self._update_flags(result)
                self.stats['arith_ops'] += 1
        
        elif opcode == Opcode.MUL3:
            # MUL3 Rdest, Rsrc1, Rsrc2 - Balanced ternary multiply
            dest = f"R{instr.arg1}"
            src1 = f"R{instr.arg2}"
            src2 = f"R{instr.arg3}"
            
            v1 = self.registers.read(src1)
            v2 = self.registers.read(src2)
            if v1 and v2:
                result = BalancedTernaryArithmetic.multiply(v1, v2)
                self.registers.write(dest, result)
                self._update_flags(result)
                self.stats['arith_ops'] += 1
        
        elif opcode == Opcode.NEG:
            # NEG Rdest, Rsrc - Negate
            dest = f"R{instr.arg1}"
            src = f"R{instr.arg2}"
            
            value = self.registers.read(src)
            if value:
                result = -value
                self.registers.write(dest, result)
                self._update_flags(result)
                self.stats['arith_ops'] += 1
        
        elif opcode == Opcode.CMP:
            # CMP Rsrc1, Rsrc2 - Compare
            src1 = f"R{instr.arg1}"
            src2 = f"R{instr.arg2}"
            
            v1 = self.registers.read(src1)
            v2 = self.registers.read(src2)
            if v1 and v2:
                result = BalancedTernaryArithmetic.compare(v1, v2)
                # Set flags based on comparison
                if result == NEG:
                    self.registers.set_flag('N', POS)
                    self.registers.set_flag('Z', ZERO)
                    self.registers.set_flag('P', ZERO)
                elif result == ZERO:
                    self.registers.set_flag('N', ZERO)
                    self.registers.set_flag('Z', POS)
                    self.registers.set_flag('P', ZERO)
                else:  # POS
                    self.registers.set_flag('N', ZERO)
                    self.registers.set_flag('Z', ZERO)
                    self.registers.set_flag('P', POS)
        
        elif opcode == Opcode.JNEG:
            # JNEG addr - Jump if negative flag set
            self.stats['jumps'] += 1
            flags = self.registers.get_flags()
            if flags['N'] == POS or flags['N'] == NEG:
                self.registers.write('PC', TritVector(value=instr.arg1))
                self.stats['branches_taken'] += 1
        
        elif opcode == Opcode.JZERO:
            # JZERO addr - Jump if zero flag set
            self.stats['jumps'] += 1
            flags = self.registers.get_flags()
            if flags['Z'] == POS:
                self.registers.write('PC', TritVector(value=instr.arg1))
                self.stats['branches_taken'] += 1
        
        elif opcode == Opcode.JPOS:
            # JPOS addr - Jump if positive flag set
            self.stats['jumps'] += 1
            flags = self.registers.get_flags()
            if flags['P'] == POS:
                self.registers.write('PC', TritVector(value=instr.arg1))
                self.stats['branches_taken'] += 1
        
        elif opcode == Opcode.JMP:
            # JMP addr - Unconditional jump
            self.registers.write('PC', TritVector(value=instr.arg1))
            self.stats['jumps'] += 1
            self.stats['branches_taken'] += 1
        
        elif opcode == Opcode.AND3:
            # AND3 Rdest, Rsrc1, Rsrc2 - Ternary AND
            dest = f"R{instr.arg1}"
            src1 = f"R{instr.arg2}"
            src2 = f"R{instr.arg3}"
            
            v1 = self.registers.read(src1)
            v2 = self.registers.read(src2)
            if v1 and v2:
                # Convert to trits and apply logic (simplified for single trit)
                result_trit = TernaryLogic.AND(
                    Trit(v1.to_int() % 3 - 1) if v1.to_int() != 0 else ZERO,
                    Trit(v2.to_int() % 3 - 1) if v2.to_int() != 0 else ZERO
                )
                result = TritVector(value=result_trit.to_int())
                self.registers.write(dest, result)
        
        elif opcode == Opcode.OR3:
            # OR3 Rdest, Rsrc1, Rsrc2 - Ternary OR
            dest = f"R{instr.arg1}"
            src1 = f"R{instr.arg2}"
            src2 = f"R{instr.arg3}"
            
            v1 = self.registers.read(src1)
            v2 = self.registers.read(src2)
            if v1 and v2:
                result_trit = TernaryLogic.OR(
                    Trit(v1.to_int() % 3 - 1) if v1.to_int() != 0 else ZERO,
                    Trit(v2.to_int() % 3 - 1) if v2.to_int() != 0 else ZERO
                )
                result = TritVector(value=result_trit.to_int())
                self.registers.write(dest, result)
        
        elif opcode == Opcode.XOR3:
            # XOR3 Rdest, Rsrc1, Rsrc2 - Ternary XOR
            dest = f"R{instr.arg1}"
            src1 = f"R{instr.arg2}"
            src2 = f"R{instr.arg3}"
            
            v1 = self.registers.read(src1)
            v2 = self.registers.read(src2)
            if v1 and v2:
                result_trit = TernaryLogic.XOR(
                    Trit(v1.to_int() % 3 - 1) if v1.to_int() != 0 else ZERO,
                    Trit(v2.to_int() % 3 - 1) if v2.to_int() != 0 else ZERO
                )
                result = TritVector(value=result_trit.to_int())
                self.registers.write(dest, result)
    
    def _update_flags(self, value: TritVector):
        """Update status flags based on result value."""
        val = value.to_int()
        
        if val < 0:
            self.registers.set_flag('N', POS)
            self.registers.set_flag('Z', ZERO)
            self.registers.set_flag('P', ZERO)
        elif val > 0:
            self.registers.set_flag('N', ZERO)
            self.registers.set_flag('Z', ZERO)
            self.registers.set_flag('P', POS)
        else:
            self.registers.set_flag('N', ZERO)
            self.registers.set_flag('Z', POS)
            self.registers.set_flag('P', ZERO)
    
    def get_stats(self) -> Dict[str, int]:
        """Get execution statistics."""
        return {
            **self.stats,
            'cycles': self.cycle_count,
            'instructions': self.instructions_executed,
        }


if __name__ == "__main__":
    print("=== Balanced Ternary CPU Demo ===\n")
    
    # Create CPU
    cpu = TernaryCPU(num_registers=27, memory_size=729)
    
    # Create a simple program: Add 5 + 3 and store result
    program = [
        # LOAD R0, 10  (address 10 has value 5)
        Instruction(Opcode.LOAD, 0, 10, 0),
        # LOAD R1, 11  (address 11 has value 3)
        Instruction(Opcode.LOAD, 1, 11, 0),
        # ADD3 R2, R0, R1
        Instruction(Opcode.ADD3, 2, 0, 1),
        # STORE R2, 12
        Instruction(Opcode.STORE, 2, 12, 0),
        # HALT
        Instruction(Opcode.HALT, 0, 0, 0),
    ]
    
    # Load program into memory starting at address 0
    cpu.memory.load_program(program, start_addr=0)
    
    # Initialize data at addresses 10, 11
    cpu.memory.write(10, TritVector(value=5))
    cpu.memory.write(11, TritVector(value=3))
    
    print("Initial state:")
    print(f"  Memory[10] = {cpu.memory.read(10)} (5)")
    print(f"  Memory[11] = {cpu.memory.read(11)} (3)")
    print()
    
    # Run program
    print("Executing program...")
    cpu.run()
    
    print("\nFinal state:")
    print(f"  R0 = {cpu.registers.read('R0')} ({cpu.registers.read('R0').to_int()})")
    print(f"  R1 = {cpu.registers.read('R1')} ({cpu.registers.read('R1').to_int()})")
    print(f"  R2 = {cpu.registers.read('R2')} ({cpu.registers.read('R2').to_int()})")
    print(f"  Memory[12] = {cpu.memory.read(12)} ({cpu.memory.read(12).to_int()})")
    
    print("\nExecution statistics:")
    stats = cpu.get_stats()
    for stat_name, value in stats.items():
        print(f"  {stat_name}: {value}")
    
    print("\n" + cpu.registers.dump())
