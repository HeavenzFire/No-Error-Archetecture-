"""
Hyper-Dimensional Syntropic Execution Fabric (HD-SEF)
Core Kernel Engine

Integrates:
1. 729-Node Attractor Hyper-Space (3^6 topology)
2. Phase-Conjugate Resonance (Complex Phase Vectors)
3. Harmonic Entrainment (Golden Ratio Clocking)

This kernel replaces linear memory with topological basins of attraction.
"""

import numpy as np
import cmath
import time
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

# =============================================================================
# CONSTANTS & TYPES
# =============================================================================

class Trit(Enum):
    FALSE = -1
    NEUTRAL = 0
    TRUE = 1

PHASE_MAP = {
    Trit.FALSE: -2 * np.pi / 3,   # -120 degrees
    Trit.NEUTRAL: 0.0,            # 0 degrees
    Trit.TRUE: 2 * np.pi / 3      # +120 degrees
}

INVERSE_PHASE_MAP = {v: k for k, v in PHASE_MAP.items()}

GOLDEN_RATIO = 1.618033988749895
BASE_FREQUENCY = 1.0  # Hz
DIMENSIONS = 6
TOTAL_STATES = 3 ** DIMENSIONS  # 729

@dataclass
class ComplexTrit:
    """A trit encoded as a complex phase vector."""
    value: Trit
    phase: complex
    
    @classmethod
    def from_trit(cls, t: Trit) -> 'ComplexTrit':
        angle = PHASE_MAP[t]
        return cls(value=t, phase=cmath.exp(1j * angle))
    
    @classmethod
    def from_phase(cls, phase: complex) -> 'ComplexTrit':
        angle = cmath.phase(phase)
        # Normalize angle to [-pi, pi]
        if angle > np.pi:
            angle -= 2 * np.pi
        elif angle < -np.pi:
            angle += 2 * np.pi
            
        # Find closest standard phase
        closest_angle = min(PHASE_MAP.values(), key=lambda x: abs(x - angle))
        trit_val = INVERSE_PHASE_MAP[closest_angle]
        return cls(value=trit_val, phase=cmath.exp(1j * closest_angle))
    
    def conjugate(self) -> 'ComplexTrit':
        return ComplexTrit(value=self.value, phase=self.phase.conjugate())

# =============================================================================
# HARMONIC CLOCK
# =============================================================================

class HarmonicClock:
    """
    Drives system evolution using Golden Ratio harmonic locking.
    Replaces arbitrary setInterval polling with continuous wave synchronization.
    """
    
    def __init__(self, base_freq: float = BASE_FREQUENCY):
        self.base_freq = base_freq
        self.start_time = time.time()
        self.harmonics = [
            1.0,                   # Fundamental
            GOLDEN_RATIO,          # Phi
            GOLDEN_RATIO ** 2,     # Phi^2
            1.5,                   # Perfect Fifth
            2.0                    # Octave
        ]
        
    def get_phase(self, harmonic_index: int = 0) -> float:
        """Get current phase angle for a specific harmonic."""
        freq = self.base_freq * self.harmonics[harmonic_index % len(self.harmonics)]
        elapsed = time.time() - self.start_time
        return 2 * np.pi * freq * elapsed
    
    def get_coherence_window(self, tolerance: float = 0.1) -> bool:
        """
        Check if current time aligns with a constructive interference peak.
        Returns True if system is in a 'high coherence' temporal window.
        """
        # Sum of harmonics
        signal = sum(np.sin(self.get_phase(i)) for i in range(len(self.harmonics)))
        normalized = signal / len(self.harmonics)
        return abs(normalized) > (1.0 - tolerance)
    
    def wait_for_cycle(self, harmonic_index: int = 0):
        """Block until next peak of specified harmonic."""
        current_phase = self.get_phase(harmonic_index)
        target_phase = ((current_phase // (2 * np.pi)) + 1) * 2 * np.pi
        freq = self.base_freq * self.harmonics[harmonic_index % len(self.harmonics)]
        wait_time = (target_phase - current_phase) / (2 * np.pi * freq)
        if wait_time > 0:
            time.sleep(wait_time)

# =============================================================================
# PHASE-CONJUGATE RESONANCE ENGINE
# =============================================================================

class PhaseConjugateEngine:
    """
    Performs logic operations via complex phase interference.
    Noise cancellation occurs naturally through conjugate multiplication.
    """
    
    @staticmethod
    def interfere(states: List[ComplexTrit]) -> ComplexTrit:
        """
        Constructive/destructive interference of multiple phase vectors.
        Returns the resultant vector collapsed back to a balanced trit.
        """
        if not states:
            return ComplexTrit.from_trit(Trit.NEUTRAL)
            
        resultant = sum(s.phase for s in states)
        return ComplexTrit.from_phase(resultant)
    
    @staticmethod
    def conjugate_cancel(signal: ComplexTrit, noise: ComplexTrit) -> ComplexTrit:
        """
        Cancel noise by multiplying signal with noise conjugate.
        If noise == signal, result is real (magnitude squared), eliminating phase error.
        """
        cleaned = signal.phase * noise.conjugate().phase
        return ComplexTrit.from_phase(cleaned)
    
    @staticmethod
    def amplify(coherent_signals: List[ComplexTrit]) -> ComplexTrit:
        """
        Amplify coherent signals. If all phases align, magnitude grows linearly.
        """
        if not coherent_signals:
            return ComplexTrit.from_trit(Trit.NEUTRAL)
            
        summed = sum(s.phase for s in coherent_signals)
        # Normalization not needed here; magnitude indicates confidence
        return ComplexTrit.from_phase(summed)

# =============================================================================
# 729-NODE ATTRACTOR HYPER-SPACE
# =============================================================================

class AttractorHyperSpace:
    """
    The core memory and logic fabric.
    729 nodes arranged in a 6-dimensional ternary hypercube.
    States evolve by sliding down energy gradients into basins of attraction.
    """
    
    def __init__(self):
        self.dimensions = DIMENSIONS
        self.total_nodes = TOTAL_STATES
        self.basins: Dict[int, List[int]] = {}  # Map attractor ID -> list of member states
        self.energy_landscape = np.zeros(TOTAL_STATES)
        self.state_vector = np.zeros(DIMENSIONS, dtype=int)  # Current position (-1, 0, 1)
        
        # Initialize random attractors for demonstration
        self._initialize_landscape()
        
    def _index_from_state(self, state: np.ndarray) -> int:
        """Convert 6-dim ternary array to linear index (0-728)."""
        index = 0
        multiplier = 1
        for val in state:
            index += (val + 1) * multiplier  # Shift -1,0,1 to 0,1,2
            multiplier *= 3
        return index
    
    def _state_from_index(self, index: int) -> np.ndarray:
        """Convert linear index back to 6-dim ternary array."""
        state = np.zeros(DIMENSIONS, dtype=int)
        temp = index
        for i in range(DIMENSIONS):
            val = (temp % 3) - 1  # Shift 0,1,2 back to -1,0,1
            state[i] = val
            temp //= 3
        return state
    
    def _initialize_landscape(self, num_attractors: int = 15):
        """Create random attractor basins."""
        attractor_indices = np.random.choice(TOTAL_STATES, num_attractors, replace=False)
        
        for i, attr_idx in enumerate(attractor_indices):
            self.basins[attr_idx] = []
            self.energy_landscape[attr_idx] = -1.0 * (i + 1)  # Deeper energy for later attractors
            
        # Assign every node to its nearest attractor (simple Euclidean in ternary space)
        for idx in range(TOTAL_STATES):
            state = self._state_from_index(idx)
            min_dist = float('inf')
            nearest_attr = -1
            
            for attr_idx in attractor_indices:
                attr_state = self._state_from_index(attr_idx)
                dist = np.sum((state - attr_state) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_attr = attr_idx
            
            if nearest_attr != -1:
                self.basins[nearest_attr].append(idx)
                # Energy increases with distance from attractor
                self.energy_landscape[idx] = min_dist * 0.1

    def project_to_phase_space(self, state: np.ndarray) -> List[ComplexTrit]:
        """Map a 6-dim state to 6 complex phase vectors."""
        return [ComplexTrit.from_trit(Trit(val)) for val in state]
    
    def collapse_from_phase_space(self, phases: List[ComplexTrit]) -> np.ndarray:
        """Map 6 complex phase vectors back to 6-dim ternary state."""
        return np.array([p.value.value for p in phases])
    
    def step(self, noise_level: float = 0.0) -> Tuple[np.ndarray, float]:
        """
        Evolve state one step towards nearest attractor.
        Optionally inject phase noise before collapsing.
        Returns (new_state, energy_delta).
        """
        current_idx = self._index_from_state(self.state_vector)
        current_energy = self.energy_landscape[current_idx]
        
        # Find nearest attractor
        nearest_attr = -1
        for attr_idx, members in self.basins.items():
            if current_idx in members:
                nearest_attr = attr_idx
                break
        
        if nearest_attr == -1:
            return self.state_vector, 0.0
            
        target_state = self._state_from_index(nearest_attr)
        
        # Move one trit closer to target (Manhattan distance in ternary space)
        new_state = self.state_vector.copy()
        for i in range(DIMENSIONS):
            if new_state[i] != target_state[i]:
                if new_state[i] < target_state[i]:
                    new_state[i] += 1
                else:
                    new_state[i] -= 1
                break  # Only change one dimension per step
        
        # Apply phase noise if requested
        if noise_level > 0:
            phases = self.project_to_phase_space(new_state)
            noisy_phases = []
            for p in phases:
                if np.random.random() < noise_level:
                    # Rotate phase randomly
                    rotation = cmath.exp(1j * np.random.uniform(-np.pi/3, np.pi/3))
                    noisy_phases.append(ComplexTrit.from_phase(p.phase * rotation))
                else:
                    noisy_phases.append(p)
            new_state = self.collapse_from_phase_space(noisy_phases)
        
        new_idx = self._index_from_state(new_state)
        new_energy = self.energy_landscape[new_idx]
        
        self.state_vector = new_state
        return new_state, new_energy - current_energy
    
    def get_syntropy_metric(self) -> float:
        """
        Calculate global syntropic coherence.
        Returns value between 0.0 (max entropic) and 1.0 (max syntropic).
        """
        current_idx = self._index_from_state(self.state_vector)
        energy = self.energy_landscape[current_idx]
        
        # Normalize: min energy is approx -15, max is positive distance
        # Map to 0-1 range where lower energy = higher syntropy
        min_e = np.min(self.energy_landscape)
        max_e = np.max(self.energy_landscape)
        
        if max_e == min_e:
            return 0.5
            
        # Invert so low energy = high syntropy
        syntropy = 1.0 - ((energy - min_e) / (max_e - min_e))
        return syntropy

# =============================================================================
# HD-SEF KERNEL ORCHESTRATOR
# =============================================================================

class HDSEFKernel:
    """
    The unified execution fabric.
    Combines Attractor Space, Phase Conjugation, and Harmonic Clocking.
    """
    
    def __init__(self):
        self.space = AttractorHyperSpace()
        self.clock = HarmonicClock()
        self.engine = PhaseConjugateEngine()
        self.running = False
        self.history: List[Dict] = []
        
    def run_cycle(self, inject_noise: float = 0.0) -> Dict:
        """Execute one harmonic cycle."""
        # Wait for coherence window
        if not self.clock.get_coherence_window():
            # Optional: force step anyway or skip
            pass
            
        # Get current state in phase representation
        current_state = self.space.state_vector
        phases = self.space.project_to_phase_space(current_state)
        
        # Apply phase-conjugate noise cancellation if noise injected
        if inject_noise > 0:
            # Simulate noise vector
            noise_phases = [
                ComplexTrit.from_phase(cmath.exp(1j * np.random.uniform(-0.5, 0.5)))
                for _ in range(DIMENSIONS)
            ]
            # Cancel noise
            cleaned_phases = [
                self.engine.conjugate_cancel(sig, noise)
                for sig, noise in zip(phases, noise_phases)
            ]
            # Interference step could go here
            final_phases = cleaned_phases
        else:
            final_phases = phases
            
        # Collapse back to ternary and step towards attractor
        collapsed = self.space.collapse_from_phase_space(final_phases)
        self.space.state_vector = collapsed  # Reset to cleaned state
        
        new_state, energy_delta = self.space.step(noise_level=inject_noise)
        syntropy = self.space.get_syntropy_metric()
        
        record = {
            'time': time.time(),
            'state': new_state.tolist(),
            'energy_delta': energy_delta,
            'syntropy': syntropy,
            'coherent': self.clock.get_coherence_window()
        }
        self.history.append(record)
        return record
    
    def run(self, cycles: int, noise_profile: List[float] = None):
        """Run multiple cycles."""
        self.running = True
        results = []
        
        for i in range(cycles):
            noise = 0.0
            if noise_profile and i < len(noise_profile):
                noise = noise_profile[i]
                
            result = self.run_cycle(inject_noise=noise)
            results.append(result)
            
            # Optional: Sleep based on harmonic rhythm instead of fixed time
            # self.clock.wait_for_cycle(harmonic_index=i % 5)
            
        self.running = False
        return results

# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    print("=== Hyper-Dimensional Syntropic Execution Fabric (HD-SEF) ===\n")
    
    kernel = HDSEFKernel()
    
    print(f"Initialized 729-node attractor space ({DIMENSIONS} dimensions)")
    print(f"Base Frequency: {BASE_FREQUENCY} Hz (Golden Ratio scaled)")
    print(f"Phase Encoding: {-120}°, 0°, +{120}°\n")
    
    # Run simulation with increasing noise
    noise_ramp = [0.0] * 10 + [0.1] * 10 + [0.3] * 10 + [0.5] * 10
    
    print("Executing 40 harmonic cycles with ramping noise...")
    results = kernel.run(40, noise_profile=noise_ramp)
    
    # Analyze results
    avg_syntropy = sum(r['syntropy'] for r in results) / len(results)
    recovery_count = sum(1 for r in results if r['syntropy'] > 0.8)
    
    print(f"\n--- Execution Summary ---")
    print(f"Total Cycles: {len(results)}")
    print(f"Average Syntropy: {avg_syntropy:.4f}")
    print(f"High-Coherence Cycles (>0.8): {recovery_count}/{len(results)}")
    print(f"Noise Resilience: {(recovery_count/len(results))*100:.1f}%")
    
    # Show last few states
    print(f"\nFinal State Trajectory:")
    for r in results[-5:]:
        state_str = "".join(['-' if x==-1 else ('0' if x==0 else '+') for x in r['state']])
        print(f"  [{state_str}] Syntropy: {r['syntropy']:.3f} | Coherent: {r['coherent']}")
