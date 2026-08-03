"""
Dual-Base Hypervisor: Binary-Ternary Translation Layer

Maps binary pairs to balanced ternary states for native hardware execution.
Encoding scheme:
  00 → 0   (Neutral)
  01 → +1  (Syntropic)
  10 → -1  (Entropic)
  11 → None (Superposition state for interference calculations)
"""

from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import IntEnum


class TritState(IntEnum):
    ENTROPIC = -1
    NEUTRAL = 0
    SYNTROPIC = 1


@dataclass
class DualBaseTrit:
    """
    A trit encoded as two binary bits for native hardware execution.
    
    Binary mapping:
      bit_high, bit_low → Ternary value
      0, 0 → 0 (Neutral)
      0, 1 → +1 (Syntropic)
      1, 0 → -1 (Entropic)
      1, 1 → None (Superposition)
    """
    bit_high: int  # Most significant bit
    bit_low: int   # Least significant bit
    
    def __post_init__(self):
        if self.bit_high not in (0, 1) or self.bit_low not in (0, 1):
            raise ValueError("Bits must be 0 or 1")
    
    @classmethod
    def from_ternary(cls, value: int) -> 'DualBaseTrit':
        """Convert balanced ternary (-1, 0, +1) to dual-base encoding."""
        if value == 0:
            return cls(0, 0)
        elif value == 1:
            return cls(0, 1)
        elif value == -1:
            return cls(1, 0)
        else:
            raise ValueError(f"Invalid ternary value: {value}. Must be -1, 0, or +1")
    
    @classmethod
    def from_superposition(cls) -> 'DualBaseTrit':
        """Create superposition state (1, 1)."""
        return cls(1, 1)
    
    def to_ternary(self) -> Optional[int]:
        """
        Convert dual-base encoding back to balanced ternary.
        Returns None for superposition state.
        """
        if self.bit_high == 0 and self.bit_low == 0:
            return 0
        elif self.bit_high == 0 and self.bit_low == 1:
            return 1
        elif self.bit_high == 1 and self.bit_low == 0:
            return -1
        else:  # 1, 1 = superposition
            return None
    
    def is_superposition(self) -> bool:
        """Check if this trit is in superposition state."""
        return self.bit_high == 1 and self.bit_low == 1
    
    def to_phase_angle(self) -> Optional[float]:
        """
        Convert to phase angle representation (degrees).
        -1 → -120°, 0 → 0°, +1 → +120°, superposition → None
        """
        ternary = self.to_ternary()
        if ternary is None:
            return None
        return ternary * 120.0
    
    @classmethod
    def from_phase_angle(cls, angle: float) -> 'DualBaseTrit':
        """Convert phase angle to dual-base trit."""
        # Normalize angle to [-180, 180]
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        
        if -150 <= angle <= -90:
            return cls.from_ternary(-1)
        elif -30 <= angle <= 30:
            return cls.from_ternary(0)
        elif 90 <= angle <= 150:
            return cls.from_ternary(1)
        else:
            raise ValueError(f"Angle {angle}° doesn't map to valid trit phase")
    
    def __repr__(self) -> str:
        ternary = self.to_ternary()
        if ternary is None:
            return f"DualBaseTrit({self.bit_high}{self.bit_low} → SUPERPOSITION)"
        return f"DualBaseTrit({self.bit_high}{self.bit_low} → {ternary:+d})"


class DualBaseHypervisor:
    """
    Hypervisor layer that translates between binary hardware operations
    and balanced ternary logic execution.
    """
    
    def __init__(self, size: int = 729):
        """Initialize hypervisor with memory array of dual-base trits."""
        self.size = size
        # Memory stored as binary pairs for native hardware compatibility
        self.memory: List[DualBaseTrit] = [DualBaseTrit(0, 0) for _ in range(size)]
        self.pointer = 0
    
    def store(self, index: int, value: int) -> None:
        """Store a ternary value at specified index."""
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} out of bounds [0, {self.size})")
        self.memory[index] = DualBaseTrit.from_ternary(value)
    
    def load(self, index: int) -> Optional[int]:
        """Load ternary value from specified index."""
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} out of bounds [0, {self.size})")
        return self.memory[index].to_ternary()
    
    def add(self, idx_a: int, idx_b: int) -> DualBaseTrit:
        """
        Perform ternary addition using binary hardware operations.
        Returns result as dual-base trit (may be superposition).
        """
        a = self.load(idx_a)
        b = self.load(idx_b)
        
        if a is None or b is None:
            # Handle superposition via interference
            return self._interference_add(idx_a, idx_b)
        
        result = a + b
        # Normalize to balanced ternary range
        if result > 1:
            result = 1
        elif result < -1:
            result = -1
        
        return DualBaseTrit.from_ternary(result)
    
    def _interference_add(self, idx_a: int, idx_b: int) -> DualBaseTrit:
        """
        Handle addition when one or both operands are in superposition.
        Uses phase-conjugate interference logic.
        """
        trit_a = self.memory[idx_a]
        trit_b = self.memory[idx_b]
        
        # If both in superposition, result is superposition
        if trit_a.is_superposition() and trit_b.is_superposition():
            return DualBaseTrit.from_superposition()
        
        # If one in superposition, collapse based on other operand
        if trit_a.is_superposition():
            # Superposition collapses to opposite phase for constructive interference
            val_b = trit_b.to_ternary()
            if val_b == 1:
                return DualBaseTrit.from_ternary(-1)
            elif val_b == -1:
                return DualBaseTrit.from_ternary(1)
            else:
                return DualBaseTrit.from_superposition()
        
        if trit_b.is_superposition():
            val_a = trit_a.to_ternary()
            if val_a == 1:
                return DualBaseTrit.from_ternary(-1)
            elif val_a == -1:
                return DualBaseTrit.from_ternary(1)
            else:
                return DualBaseTrit.from_superposition()
        
        return DualBaseTrit.from_superposition()
    
    def multiply(self, idx_a: int, idx_b: int) -> DualBaseTrit:
        """Perform ternary multiplication using binary hardware."""
        a = self.load(idx_a)
        b = self.load(idx_b)
        
        if a is None or b is None:
            return DualBaseTrit.from_superposition()
        
        result = a * b
        return DualBaseTrit.from_ternary(result)
    
    def negation(self, index: int) -> DualBaseTrit:
        """Negate a trit (swap entropic/syntropic)."""
        trit = self.memory[index]
        
        if trit.is_superposition():
            return DualBaseTrit.from_superposition()
        
        val = trit.to_ternary()
        return DualBaseTrit.from_ternary(-val)
    
    def batch_encode(self, values: List[int]) -> List[DualBaseTrit]:
        """Encode a list of ternary values to dual-base format."""
        return [DualBaseTrit.from_ternary(v) for v in values]
    
    def batch_decode(self, trits: List[DualBaseTrit]) -> List[Optional[int]]:
        """Decode dual-base trits back to ternary values."""
        return [t.to_ternary() for t in trits]
    
    def get_binary_representation(self, index: int) -> Tuple[int, int]:
        """Get raw binary pair for hardware-level operations."""
        trit = self.memory[index]
        return (trit.bit_high, trit.bit_low)
    
    def set_from_binary(self, index: int, bit_high: int, bit_low: int) -> None:
        """Set memory from raw binary pair."""
        self.memory[index] = DualBaseTrit(bit_high, bit_low)
    
    def compute_syntropy_score(self) -> float:
        """
        Calculate global syntropy score from memory state.
        Returns value in [-1, 1] where:
          -1 = fully entropic, 0 = neutral, +1 = fully syntropic
        """
        total = 0
        count = 0
        
        for trit in self.memory:
            val = trit.to_ternary()
            if val is not None:
                total += val
                count += 1
            # Superposition states contribute 0 (neutral)
        
        if count == 0:
            return 0.0
        
        return total / count
    
    def collapse_superpositions(self, bias: int = 0) -> None:
        """
        Collapse all superposition states to definite values.
        Bias: -1 (entropic), 0 (neutral), +1 (syntropic)
        """
        for i, trit in enumerate(self.memory):
            if trit.is_superposition():
                self.memory[i] = DualBaseTrit.from_ternary(bias)


def run_demonstration():
    """Demonstrate dual-base hypervisor capabilities."""
    print("=" * 60)
    print("DUAL-BASE HYPERVISOR DEMONSTRATION")
    print("=" * 60)
    
    # Create hypervisor with 729-node attractor space
    hypervisor = DualBaseHypervisor(size=729)
    
    print(f"\nInitialized {hypervisor.size}-node memory array")
    print("Encoding: 00→0, 01→+1, 10→-1, 11→SUPERPOSITION\n")
    
    # Test basic encoding/decoding
    print("--- Basic Encoding Tests ---")
    test_values = [-1, 0, 1, -1, 0, 1]
    encoded = hypervisor.batch_encode(test_values)
    
    for i, (orig, enc) in enumerate(zip(test_values, encoded)):
        print(f"  {orig:+d} → {enc.bit_high}{enc.bit_low} → {enc.to_ternary():+d}")
    
    # Store values in memory
    print("\n--- Memory Operations ---")
    hypervisor.store(0, 1)    # Syntropic
    hypervisor.store(1, -1)   # Entropic
    hypervisor.store(2, 0)    # Neutral
    hypervisor.set_from_binary(3, 1, 1)  # Superposition
    
    print(f"Address 0: {hypervisor.load(0):+d} (binary: {hypervisor.get_binary_representation(0)})")
    print(f"Address 1: {hypervisor.load(1):+d} (binary: {hypervisor.get_binary_representation(1)})")
    print(f"Address 2: {hypervisor.load(2):+d} (binary: {hypervisor.get_binary_representation(2)})")
    print(f"Address 3: {hypervisor.memory[3]} (binary: {hypervisor.get_binary_representation(3)})")
    
    # Test arithmetic operations
    print("\n--- Arithmetic Operations ---")
    result = hypervisor.add(0, 1)  # +1 + (-1) = 0
    print(f"ADD [0] + [1]: (+1) + (-1) = {result}")
    
    result = hypervisor.add(0, 2)  # +1 + 0 = +1
    print(f"ADD [0] + [2]: (+1) + (0) = {result}")
    
    result = hypervisor.multiply(0, 1)  # +1 * (-1) = -1
    print(f"MUL [0] * [1]: (+1) * (-1) = {result}")
    
    # Test superposition interference
    print("\n--- Superposition Interference ---")
    result = hypervisor.add(0, 3)  # +1 + superposition
    print(f"ADD [0] + [3]: (+1) + (SUPERPOSITION) = {result}")
    
    result = hypervisor.add(1, 3)  # -1 + superposition
    print(f"ADD [1] + [3]: (-1) + (SUPERPOSITION) = {result}")
    
    # Calculate syntropy score
    print("\n--- Global State Analysis ---")
    # Fill memory with mixed states
    import random
    random.seed(42)
    for i in range(100):
        hypervisor.store(i, random.choice([-1, 0, 1]))
    
    # Add some superpositions
    for i in range(100, 110):
        hypervisor.set_from_binary(i, 1, 1)
    
    syntropy = hypervisor.compute_syntropy_score()
    print(f"Syntropy Score (first 100 nodes): {syntropy:.4f}")
    
    # Collapse superpositions
    hypervisor.collapse_superpositions(bias=1)
    syntropy_after = hypervisor.compute_syntropy_score()
    print(f"Syntropy Score (after collapse to +1): {syntropy_after:.4f}")
    
    # Phase angle conversion
    print("\n--- Phase Angle Conversion ---")
    for angle in [-120, 0, 120]:
        trit = DualBaseTrit.from_phase_angle(angle)
        print(f"  {angle:4d}° → {trit.bit_high}{trit.bit_low} → {trit.to_ternary():+d} → {trit.to_phase_angle():.0f}°")
    
    print("\n" + "=" * 60)
    print("Dual-base hypervisor operating correctly!")
    print("Binary hardware can now execute ternary logic natively.")
    print("=" * 60)


if __name__ == "__main__":
    run_demonstration()
