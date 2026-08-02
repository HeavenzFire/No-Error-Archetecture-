"""
Balanced Ternary Register File

Implements a register file for the balanced ternary CPU:
- Configurable number of registers
- Read/write operations
- Register status tracking
- Support for special registers (PC, SP, etc.)
"""

from typing import Dict, List, Optional, Tuple
from trit_core.trit import Trit, NEG, ZERO, POS
from trit_core.arithmetic import TritVector


class Register:
    """
    A single balanced ternary register.
    
    Holds a TritVector value and supports read/write operations.
    """
    
    def __init__(self, name: str = "R0", width: int = 9):
        """
        Initialize a register.
        
        Args:
            name: Register name/identifier
            width: Number of trits in the register (default 9 = ~14 bits equivalent)
        """
        self.name = name
        self.width = width
        self.value = TritVector(value=0)
        self.dirty = False
        self.valid = True
    
    def read(self) -> TritVector:
        """Read the register value."""
        return self.value.copy()
    
    def write(self, value: TritVector) -> bool:
        """
        Write a value to the register.
        
        Args:
            value: TritVector to write
            
        Returns:
            True if successful, False if value exceeds register width
        """
        # Check if value fits in register
        if len(value.trits) > self.width:
            return False
        
        self.value = value.copy()
        self.dirty = True
        return True
    
    def clear(self):
        """Clear the register (set to zero)."""
        self.value = TritVector(value=0)
        self.dirty = False
    
    def __repr__(self) -> str:
        return f"Register({self.name}={self.value})"


class RegisterFile:
    """
    Balanced ternary register file.
    
    Provides access to multiple registers with indexed addressing.
    """
    
    # Special register names
    SPECIAL_REGISTERS = {
        'PC': 'Program Counter',
        'SP': 'Stack Pointer',
        'AC': 'Accumulator',
        'IR': 'Instruction Register',
        'FLAGS': 'Status Flags',
    }
    
    def __init__(self, num_registers: int = 27, register_width: int = 9):
        """
        Initialize the register file.
        
        Args:
            num_registers: Total number of general-purpose registers
            register_width: Width of each register in trits
        """
        self.num_registers = num_registers
        self.register_width = register_width
        self.registers: Dict[str, Register] = {}
        
        # Create general-purpose registers (R0, R1, ..., Rn)
        for i in range(num_registers):
            reg_name = f"R{i}"
            self.registers[reg_name] = Register(name=reg_name, width=register_width)
        
        # Create special registers
        for reg_name in self.SPECIAL_REGISTERS.keys():
            self.registers[reg_name] = Register(name=reg_name, width=register_width)
        
        # Initialize PC and SP
        self.registers['PC'].write(TritVector(value=0))
        self.registers['SP'].write(TritVector(value=num_registers - 1))
    
    def get_register(self, reg_id: str) -> Optional[Register]:
        """
        Get a register by ID.
        
        Args:
            reg_id: Register name (e.g., "R0", "PC", "AC")
            
        Returns:
            Register object or None if not found
        """
        return self.registers.get(reg_id)
    
    def read(self, reg_id: str) -> Optional[TritVector]:
        """
        Read a register value.
        
        Args:
            reg_id: Register name
            
        Returns:
            TritVector value or None if register not found
        """
        reg = self.get_register(reg_id)
        if reg is None:
            return None
        return reg.read()
    
    def write(self, reg_id: str, value: TritVector) -> bool:
        """
        Write a value to a register.
        
        Args:
            reg_id: Register name
            value: TritVector to write
            
        Returns:
            True if successful, False otherwise
        """
        reg = self.get_register(reg_id)
        if reg is None:
            return False
        return reg.write(value)
    
    def increment_pc(self, amount: int = 1) -> TritVector:
        """
        Increment the program counter.
        
        Args:
            amount: Amount to increment by
            
        Returns:
            New PC value
        """
        pc = self.read('PC')
        if pc is None:
            pc = TritVector(value=0)
        
        new_pc = TritVector(value=pc.to_int() + amount)
        self.write('PC', new_pc)
        return new_pc
    
    def get_flags(self) -> Dict[str, Trit]:
        """
        Get status flags from the FLAGS register.
        
        Returns:
            Dictionary of flag names to Trit values
        """
        flags_val = self.read('FLAGS')
        if flags_val is None:
            return {'N': ZERO, 'Z': ZERO, 'P': ZERO, 'C': ZERO, 'V': ZERO}
        
        # Decode flags from trits (simplified)
        # In a real implementation, each flag would be a specific trit position
        val = flags_val.to_int()
        return {
            'N': Trit(NEG if val < 0 else (POS if val > 0 else ZERO)),  # Negative
            'Z': ZERO if val != 0 else POS,  # Zero
            'P': POS if val > 0 else ZERO,   # Positive
            'C': ZERO,  # Carry (would be set by arithmetic operations)
            'V': ZERO,  # Overflow
        }
    
    def set_flag(self, flag_name: str, value: Trit):
        """
        Set a specific flag.
        
        Args:
            flag_name: Name of flag ('N', 'Z', 'P', 'C', 'V')
            value: Trit value to set
        """
        # Simplified flag setting
        flags = self.get_flags()
        flags[flag_name] = value
        
        # Encode flags back to FLAGS register (simplified)
        flag_val = 0
        if flags['N'] == POS:
            flag_val -= 1
        elif flags['N'] == NEG:
            flag_val += 1
        
        if flags['Z'] == POS:
            flag_val += 3
        
        if flags['P'] == POS:
            flag_val += 9
        
        self.write('FLAGS', TritVector(value=flag_val))
    
    def dump(self) -> str:
        """
        Dump all register values as a string.
        
        Returns:
            Formatted string showing all register contents
        """
        lines = []
        lines.append("=" * 50)
        lines.append("REGISTER FILE DUMP")
        lines.append("=" * 50)
        
        # Special registers first
        for reg_name, description in self.SPECIAL_REGISTERS.items():
            reg = self.registers[reg_name]
            lines.append(f"{reg_name:6s} ({description:18s}): {str(reg.value):>12s} ({reg.value.to_int():6d})")
        
        lines.append("-" * 50)
        
        # General purpose registers
        regs_per_line = 3
        for i in range(0, min(18, self.num_registers), regs_per_line):
            line_parts = []
            for j in range(regs_per_line):
                if i + j < self.num_registers:
                    reg_name = f"R{i+j}"
                    reg = self.registers[reg_name]
                    line_parts.append(f"{reg_name}: {reg.value} ({reg.value.to_int():3d})")
            lines.append("  ".join(line_parts))
        
        if self.num_registers > 18:
            lines.append(f"... and {self.num_registers - 18} more registers")
        
        lines.append("=" * 50)
        return "\n".join(lines)
    
    def reset(self):
        """Reset all registers to initial state."""
        for reg in self.registers.values():
            reg.clear()
        
        # Re-initialize special registers
        self.registers['PC'].write(TritVector(value=0))
        self.registers['SP'].write(TritVector(value=self.num_registers - 1))


if __name__ == "__main__":
    print("=== Balanced Ternary Register File Demo ===\n")
    
    # Create register file with 27 registers (3^3)
    reg_file = RegisterFile(num_registers=27, register_width=9)
    
    # Write some values
    print("Writing values to registers:")
    reg_file.write('R0', TritVector(value=5))
    reg_file.write('R1', TritVector(value=-3))
    reg_file.write('R2', TritVector(value=13))
    reg_file.write('AC', TritVector(value=42))
    
    print(f"  R0 = {reg_file.read('R0')} ({reg_file.read('R0').to_int()})")
    print(f"  R1 = {reg_file.read('R1')} ({reg_file.read('R1').to_int()})")
    print(f"  R2 = {reg_file.read('R2')} ({reg_file.read('R2').to_int()})")
    print(f"  AC = {reg_file.read('AC')} ({reg_file.read('AC').to_int()})")
    
    # Increment PC
    print("\nIncrementing PC:")
    for i in range(5):
        pc = reg_file.increment_pc(1)
        print(f"  PC = {pc} ({pc.to_int()})")
    
    # Test flags
    print("\nTesting flags:")
    reg_file.write('AC', TritVector(value=-7))
    flags = reg_file.get_flags()
    print(f"  After writing -7 to AC:")
    for flag_name, flag_val in flags.items():
        print(f"    {flag_name}: {flag_val}")
    
    reg_file.write('AC', TritVector(value=0))
    flags = reg_file.get_flags()
    print(f"  After writing 0 to AC:")
    for flag_name, flag_val in flags.items():
        print(f"    {flag_name}: {flag_val}")
    
    # Full dump
    print("\n")
    print(reg_file.dump())
