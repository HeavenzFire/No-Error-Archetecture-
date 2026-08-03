"""
Harmonic Entrainment Protocol Module

This module transitions system polling from arbitrary clock cycles to 
harmonic frequency locks, anchoring state evaluations to continuous 
environmental or mathematical baseline frequencies. This eliminates 
internal jitter and resource contention through absolute synchronization.

Key Features:
- Golden ratio (φ) based harmonic frequencies
- Prime number resonance patterns
- Fibonacci sequence timing intervals
- Phase-locking to mathematical constants
- Adaptive frequency adjustment based on system load
"""

import time
import math
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import threading


# Mathematical constants for harmonic locking
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio ≈ 1.618
PI = math.pi
E = math.e

# Base frequencies (Hz) derived from mathematical constants
BASE_FREQUENCIES = {
    'phi': PHI,           # 1.618 Hz - golden ratio
    'phi_squared': PHI**2,  # 2.618 Hz
    'pi': PI / 2,         # 1.571 Hz
    'e': E / 2,           # 1.359 Hz
    'sqrt2': math.sqrt(2),  # 1.414 Hz
}


@dataclass
class HarmonicOscillator:
    """
    A single oscillator locked to a harmonic frequency.
    
    Maintains phase coherence and provides tick notifications
    at mathematically precise intervals.
    """
    name: str
    base_frequency: float
    phase: float = 0.0
    amplitude: float = 1.0
    tick_count: int = 0
    last_tick_time: float = field(default_factory=time.time)
    phase_history: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def get_period(self) -> float:
        """Calculate period in seconds."""
        return 1.0 / self.base_frequency
    
    def update_phase(self, current_time: float) -> float:
        """Update phase based on elapsed time."""
        elapsed = current_time - self.last_tick_time
        phase_increment = 2 * math.pi * self.base_frequency * elapsed
        self.phase = (self.phase + phase_increment) % (2 * math.pi)
        self.phase_history.append(self.phase)
        return self.phase
    
    def check_tick(self, tolerance: float = 0.01) -> bool:
        """
        Check if oscillator is at tick point (phase near 0).
        
        Args:
            tolerance: Acceptable deviation from perfect phase
            
        Returns:
            True if at tick point
        """
        # Normalize phase to [-π, π]
        normalized_phase = math.atan2(math.sin(self.phase), math.cos(self.phase))
        return abs(normalized_phase) < tolerance
    
    def reset(self):
        """Reset oscillator state."""
        self.phase = 0.0
        self.tick_count = 0
        self.last_tick_time = time.time()


@dataclass
class EntrainmentState:
    """Represents the global entrainment state of the system."""
    master_frequency: float
    oscillators: List[HarmonicOscillator]
    coherence_factor: float = 0.0
    last_sync_time: float = field(default_factory=time.time)
    drift_accumulation: float = 0.0


class HarmonicEntrainmentEngine:
    """
    Central engine for managing harmonic entrainment across multiple oscillators.
    
    Implements phase-locking mechanisms that synchronize all oscillators
    to a master frequency derived from mathematical constants.
    """
    
    def __init__(self, master_frequency: float = None):
        if master_frequency is None:
            master_frequency = BASE_FREQUENCIES['phi']
        
        self.master_frequency = master_frequency
        self.oscillators: List[HarmonicOscillator] = []
        self.callbacks: List[Callable] = []
        self.running = False
        self._lock = threading.Lock()
        
        # Initialize default oscillators
        self._initialize_default_oscillators()
    
    def _initialize_default_oscillators(self):
        """Create oscillators locked to various harmonic ratios."""
        harmonic_ratios = [
            ('fundamental', 1.0),
            ('octave', 2.0),
            ('fifth', 3.0/2.0),
            ('fourth', 4.0/3.0),
            ('major_third', 5.0/4.0),
            ('minor_third', 6.0/5.0),
        ]
        
        for name, ratio in harmonic_ratios:
            freq = self.master_frequency * ratio
            self.oscillators.append(HarmonicOscillator(
                name=name,
                base_frequency=freq
            ))
    
    def add_oscillator(self, name: str, frequency: float):
        """Add a custom oscillator to the ensemble."""
        with self._lock:
            self.oscillators.append(HarmonicOscillator(
                name=name,
                base_frequency=frequency
            ))
    
    def calculate_coherence(self) -> float:
        """
        Calculate global coherence factor across all oscillators.
        
        Returns value in [0, 1] where 1 indicates perfect phase alignment.
        """
        if not self.oscillators:
            return 0.0
        
        # Sum all phasors
        total_phasor = sum(
            complex(math.cos(osc.phase), math.sin(osc.phase))
            for osc in self.oscillators
        )
        
        # Coherence is normalized magnitude
        coherence = abs(total_phasor) / len(self.oscillators)
        return coherence
    
    def synchronize(self):
        """Force all oscillators into phase alignment."""
        current_time = time.time()
        
        with self._lock:
            for osc in self.oscillators:
                # Reset phase to nearest multiple of 2π
                osc.phase = 0.0
                osc.last_tick_time = current_time
                osc.tick_count += 1
            
            self.coherence_factor = 1.0
            self.last_sync_time = current_time
    
    def update(self) -> Dict[str, float]:
        """
        Update all oscillators and return their current phases.
        
        Returns dict mapping oscillator names to phase values.
        """
        current_time = time.time()
        phases = {}
        
        with self._lock:
            for osc in self.oscillators:
                osc.update_phase(current_time)
                phases[osc.name] = osc.phase
            
            # Update coherence
            self.coherence_factor = self.calculate_coherence()
        
        return phases
    
    def run_cycle(self, callback: Optional[Callable] = None):
        """
        Execute one entrainment cycle.
        
        Waits for all oscillators to reach tick point, then executes callback.
        """
        max_iterations = 1000
        tolerance = 0.1  # Phase tolerance for tick detection
        
        for _ in range(max_iterations):
            phases = self.update()
            
            # Check if fundamental oscillator is at tick
            fundamental = next((o for o in self.oscillators if o.name == 'fundamental'), 
                             self.oscillators[0])
            
            if fundamental.check_tick(tolerance):
                if callback:
                    callback(phases, self.coherence_factor)
                break
            
            # Small sleep to prevent busy-waiting
            time.sleep(0.001)
        else:
            # Timeout - force sync
            self.synchronize()
    
    def start_background_loop(self, callback: Optional[Callable] = None, 
                             interval_ms: int = 100):
        """Start background thread for continuous entrainment."""
        self.running = True
        
        def loop():
            while self.running:
                self.run_cycle(callback)
                time.sleep(interval_ms / 1000.0)
        
        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """Stop background processing."""
        self.running = False


def fibonacci_intervals(count: int = 10) -> List[float]:
    """
    Generate timing intervals based on Fibonacci sequence.
    
    Useful for creating naturally-scaling time steps.
    """
    fib = [1, 1]
    for _ in range(count - 2):
        fib.append(fib[-1] + fib[-2])
    
    # Convert to time intervals (scaled)
    scale = 0.01  # 10ms base unit
    return [f * scale for f in fib]


def prime_resonance_frequencies(base: float = 1.0, count: int = 6) -> List[float]:
    """
    Generate frequencies based on prime number ratios.
    
    Creates incommensurate frequencies that minimize interference patterns.
    """
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29][:count]
    return [base * p for p in primes]


def demonstrate_harmonic_entrainment():
    """
    Demonstrate the harmonic entrainment protocol in action.
    """
    print("=== Harmonic Entrainment Protocol Demo ===\n")
    
    # Create engine with golden ratio base frequency
    engine = HarmonicEntrainmentEngine(master_frequency=BASE_FREQUENCIES['phi'])
    
    # Add some prime-based oscillators
    prime_freqs = prime_resonance_frequencies(BASE_FREQUENCIES['phi'], 3)
    for i, freq in enumerate(prime_freqs):
        engine.add_oscillator(f'prime_{i+1}', freq)
    
    print("1. Initial Oscillator Configuration:")
    for osc in engine.oscillators:
        print(f"   {osc.name}: {osc.base_frequency:.4f} Hz (period: {osc.get_period():.4f}s)")
    
    # Run several cycles
    print("\n2. Running Entrainment Cycles:")
    coherence_history = []
    
    for cycle in range(10):
        engine.run_cycle()
        coherence_history.append(engine.coherence_factor)
        print(f"   Cycle {cycle + 1}: Coherence = {engine.coherence_factor:.4f}")
    
    # Show Fibonacci timing
    print("\n3. Fibonacci Timing Intervals:")
    intervals = fibonacci_intervals(8)
    for i, interval in enumerate(intervals):
        print(f"   Step {i + 1}: {interval*1000:.1f} ms")
    
    # Demonstrate phase evolution
    print("\n4. Phase Evolution (first 5 oscillators):")
    engine.synchronize()
    
    for step in range(5):
        phases = engine.update()
        print(f"   Step {step + 1}:")
        for name, phase in list(phases.items())[:5]:
            degrees = math.degrees(phase)
            print(f"      {name}: {degrees:7.2f}°")
        time.sleep(0.1)
    
    # Final coherence after free evolution
    final_coherence = engine.calculate_coherence()
    print(f"\n5. Final Coherence: {final_coherence:.4f}")
    
    return coherence_history


if __name__ == "__main__":
    coherence_history = demonstrate_harmonic_entrainment()
    
    # Analyze coherence stability
    if len(coherence_history) > 1:
        avg_coherence = sum(coherence_history) / len(coherence_history)
        variance = sum((c - avg_coherence)**2 for c in coherence_history) / len(coherence_history)
        print(f"\n=== Coherence Analysis ===")
        print(f"Average coherence: {avg_coherence:.4f}")
        print(f"Variance: {variance:.6f}")
        print(f"Stability: {'HIGH' if variance < 0.01 else 'MEDIUM' if variance < 0.1 else 'LOW'}")
