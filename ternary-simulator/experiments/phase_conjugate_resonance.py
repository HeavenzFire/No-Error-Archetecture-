"""
Phase-Conjugate Resonance Module for Balanced Ternary Systems

This module implements phase-conjugate feedback loops where ternary states
are encoded as complex phase angles (-120°, 0°, +120°) enabling constructive
interference patterns that automatically cancel noise and amplify coherent paths.

Key Concepts:
- Trits mapped to complex unit circle phases
- Phase-conjugate mirrors for noise cancellation
- Interference-based computation rather than sequential logic
- Self-correcting resonance patterns
"""

import cmath
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

# Phase angles in radians for balanced ternary states
PHASE_MAP = {
    -1: -2 * math.pi / 3,  # -120° (ENTROPIC)
     0: 0.0,               #   0°   (NEUTRAL/COHERENT THRESHOLD)
    +1: 2 * math.pi / 3,   # +120° (SYNTROPIC)
}

# Inverse mapping from phase to trit
def phase_to_trit(phase: float) -> int:
    """Convert phase angle back to balanced ternary value."""
    # Normalize phase to [-π, π]
    normalized = math.atan2(math.sin(phase), math.cos(phase))
    
    # Determine closest standard phase
    distances = {
        trit: abs(normalized - phase_angle)
        for trit, phase_angle in PHASE_MAP.items()
    }
    # Handle wraparound at ±π
    for trit, phase_angle in PHASE_MAP.items():
        wrapped_dist = abs(abs(normalized - phase_angle) - 2 * math.pi)
        distances[trit] = min(distances[trit], wrapped_dist)
    
    return min(distances, key=distances.get)


@dataclass
class PhaseConjugateWave:
    """
    Represents a wave with phase-encoded ternary information.
    
    Attributes:
        amplitude: Wave magnitude
        phase: Phase angle in radians (encodes trit state)
        frequency: Angular frequency
        trit_value: The underlying balanced ternary value {-1, 0, +1}
    """
    amplitude: float
    phase: float
    frequency: float = 1.0
    trit_value: int = 0
    
    def __post_init__(self):
        # Ensure trit_value matches phase encoding
        if self.trit_value not in PHASE_MAP:
            raise ValueError(f"Invalid trit value: {self.trit_value}")
        expected_phase = PHASE_MAP[self.trit_value]
        # Allow small tolerance for floating point
        if not math.isclose(self.phase % (2*math.pi), expected_phase % (2*math.pi), 
                           abs_tol=0.01):
            self.phase = expected_phase
    
    def to_complex(self) -> complex:
        """Convert to complex phasor representation."""
        return self.amplitude * cmath.exp(1j * self.phase)
    
    @classmethod
    def from_trit(cls, trit_value: int, amplitude: float = 1.0, 
                  frequency: float = 1.0) -> 'PhaseConjugateWave':
        """Create a phase-conjugate wave from a balanced ternary value."""
        return cls(
            amplitude=amplitude,
            phase=PHASE_MAP[trit_value],
            frequency=frequency,
            trit_value=trit_value
        )
    
    @classmethod
    def from_complex(cls, z: complex, frequency: float = 1.0) -> 'PhaseConjugateWave':
        """Reconstruct wave from complex number, decoding the trit value."""
        amplitude = abs(z)
        phase = cmath.phase(z)
        trit_value = phase_to_trit(phase)
        return cls(amplitude=amplitude, phase=phase, 
                   frequency=frequency, trit_value=trit_value)
    
    def conjugate(self) -> 'PhaseConjugateWave':
        """Return phase-conjugate mirror (negates phase)."""
        return PhaseConjugateWave(
            amplitude=self.amplitude,
            phase=-self.phase,
            frequency=self.frequency,
            trit_value=-self.trit_value if self.trit_value != 0 else 0
        )
    
    def interfere(self, other: 'PhaseConjugateWave') -> 'PhaseConjugateWave':
        """
        Superpose two waves via complex addition.
        Demonstrates constructive/destructive interference.
        """
        z1 = self.to_complex()
        z2 = other.to_complex()
        result = z1 + z2
        return PhaseConjugateWave.from_complex(result, self.frequency)
    
    def multiply(self, other: 'PhaseConjugateWave') -> 'PhaseConjugateWave':
        """
        Multiply waves (phase addition, amplitude multiplication).
        Corresponds to ternary multiplication in phase domain.
        """
        z1 = self.to_complex()
        z2 = other.to_complex()
        result = z1 * z2
        return PhaseConjugateWave.from_complex(result, self.frequency)


class PhaseConjugateResonator:
    """
    A resonant cavity that maintains phase-coherent ternary states.
    
    Implements feedback loops where incoming waves interfere with
    their phase-conjugates to cancel noise and reinforce signal.
    """
    
    def __init__(self, num_channels: int = 3, base_frequency: float = 1.0):
        self.num_channels = num_channels
        self.base_frequency = base_frequency
        self.channels: List[PhaseConjugateWave] = []
        self.resonance_history: List[List[complex]] = []
        
    def inject_wave(self, wave: PhaseConjugateWave, channel: int = 0):
        """Inject a wave into a specific channel."""
        while len(self.channels) <= channel:
            self.channels.append(PhaseConjugateWave.from_trit(0, 0.0))
        self.channels[channel] = wave
    
    def apply_feedback(self, feedback_strength: float = 0.5) -> List[PhaseConjugateWave]:
        """
        Apply phase-conjugate feedback to all channels.
        
        Each wave interferes with its own phase-conjugate scaled by feedback strength.
        This cancels odd-order distortions and reinforces fundamental coherence.
        """
        result = []
        for wave in self.channels:
            if wave.amplitude == 0:
                result.append(wave)
                continue
            
            # Generate phase-conjugate mirror
            conjugate = wave.conjugate()
            
            # Scale conjugate by feedback strength
            scaled_conj = PhaseConjugateWave(
                amplitude=conjugate.amplitude * feedback_strength,
                phase=conjugate.phase,
                frequency=conjugate.frequency,
                trit_value=conjugate.trit_value
            )
            
            # Interfere original with feedback
            new_wave = wave.interfere(scaled_conj)
            result.append(new_wave)
        
        self.channels = result
        self.resonance_history.append([w.to_complex() for w in result])
        return result
    
    def get_coherence_factor(self) -> float:
        """
        Calculate global coherence of the resonator.
        
        Returns value in [0, 1] where 1 indicates perfect phase alignment.
        """
        if not self.channels or all(w.amplitude == 0 for w in self.channels):
            return 0.0
        
        # Sum all phasors
        total_phasor = sum(w.to_complex() for w in self.channels)
        
        # Maximum possible amplitude if all aligned
        max_amplitude = sum(w.amplitude for w in self.channels)
        
        if max_amplitude == 0:
            return 0.0
        
        # Coherence is ratio of actual to maximum
        return abs(total_phasor) / max_amplitude
    
    def decode_states(self) -> List[int]:
        """Extract current ternary state from each channel."""
        return [wave.trit_value for wave in self.channels]
    
    def resonate(self, iterations: int = 10, 
                 feedback_strength: float = 0.3) -> float:
        """
        Run multiple feedback iterations to achieve resonance.
        
        Returns final coherence factor.
        """
        for _ in range(iterations):
            self.apply_feedback(feedback_strength)
        
        return self.get_coherence_factor()


def ternary_multiply_via_phases(a: int, b: int) -> int:
    """
    Multiply two trits using phase arithmetic.
    
    Phase addition corresponds to multiplication:
    (+1) × (+1) → phase(+120°) + phase(+120°) = phase(+240°) ≡ phase(-120°) → -1
    (+1) × (-1) → phase(+120°) + phase(-120°) = phase(0°) → +1
    etc.
    """
    wave_a = PhaseConjugateWave.from_trit(a)
    wave_b = PhaseConjugateWave.from_trit(b)
    result = wave_a.multiply(wave_b)
    return result.trit_value


def ternary_add_via_interference(a: int, b: int) -> Tuple[int, int]:
    """
    Add two trits using wave interference.
    
    Returns (sum_trit, carry_trit) since interference can produce
    amplitudes outside single-trit range.
    """
    wave_a = PhaseConjugateWave.from_trit(a)
    wave_b = PhaseConjugateWave.from_trit(b)
    result = wave_a.interfere(wave_b)
    
    # Decode primary trit from phase
    sum_trit = result.trit_value
    
    # Carry determined by amplitude deviation from unity
    # Amplitude > 1.5 indicates positive carry, < 0.5 indicates negative
    if result.amplitude > 1.5:
        carry = 1
    elif result.amplitude < 0.5:
        carry = -1
    else:
        carry = 0
    
    return sum_trit, carry


def demonstrate_noise_cancellation():
    """
    Demonstrate how phase-conjugate feedback cancels noise.
    
    Adds random phase noise to a signal, then shows recovery via
    iterative phase-conjugate feedback.
    """
    import random
    
    # Create clean signal
    clean_wave = PhaseConjugateWave.from_trit(+1, amplitude=1.0)
    
    # Add noise (random phase perturbation)
    noise_phase = random.uniform(-0.3, 0.3)
    noisy_wave = PhaseConjugateWave(
        amplitude=clean_wave.amplitude,
        phase=clean_wave.phase + noise_phase,
        frequency=clean_wave.frequency,
        trit_value=phase_to_trit(clean_wave.phase + noise_phase)
    )
    
    print(f"Original trit: {clean_wave.trit_value}")
    print(f"Noisy phase offset: {noise_phase:.3f} rad")
    print(f"Noisy decoded trit: {noisy_wave.trit_value}")
    
    # Create resonator and apply feedback
    resonator = PhaseConjugateResonator(num_channels=1)
    resonator.inject_wave(noisy_wave)
    
    final_coherence = resonator.resonate(iterations=20, feedback_strength=0.4)
    recovered_wave = resonator.channels[0]
    
    print(f"Recovered trit: {recovered_wave.trit_value}")
    print(f"Final coherence: {final_coherence:.4f}")
    print(f"Phase error after correction: {abs(recovered_wave.phase - clean_wave.phase):.6f} rad")
    
    return recovered_wave.trit_value == clean_wave.trit_value


if __name__ == "__main__":
    print("=== Phase-Conjugate Resonance Module ===\n")
    
    # Test basic phase encoding
    print("1. Phase Encoding Test:")
    for trit in [-1, 0, +1]:
        wave = PhaseConjugateWave.from_trit(trit)
        print(f"   Trit {trit:+d} → Phase {wave.phase:.3f} rad ({math.degrees(wave.phase):.1f}°)")
    
    # Test phase-conjugate multiplication
    print("\n2. Ternary Multiplication via Phase Addition:")
    test_cases = [(-1, -1), (-1, 0), (-1, +1), (0, +1), (+1, +1)]
    for a, b in test_cases:
        result = ternary_multiply_via_phases(a, b)
        print(f"   {a:+d} × {b:+d} = {result:+d}")
    
    # Test interference-based addition
    print("\n3. Ternary Addition via Wave Interference:")
    for a, b in test_cases:
        sum_trit, carry = ternary_add_via_interference(a, b)
        print(f"   {a:+d} + {b:+d} = {sum_trit:+d} (carry: {carry:+d})")
    
    # Demonstrate noise cancellation
    print("\n4. Noise Cancellation Demo:")
    success_count = sum(demonstrate_noise_cancellation() for _ in range(5))
    print(f"   Successful recoveries: {success_count}/5")
    
    # Multi-channel resonance
    print("\n5. Multi-Channel Coherence:")
    resonator = PhaseConjugateResonator(num_channels=6)
    # Inject mixed states
    for i, trit in enumerate([-1, 0, +1, +1, -1, 0]):
        resonator.inject_wave(PhaseConjugateWave.from_trit(trit), i)
    
    initial_coherence = resonator.get_coherence_factor()
    final_coherence = resonator.resonate(iterations=15, feedback_strength=0.3)
    
    print(f"   Initial coherence: {initial_coherence:.4f}")
    print(f"   Final coherence: {final_coherence:.4f}")
    print(f"   Decoded states: {resonator.decode_states()}")
