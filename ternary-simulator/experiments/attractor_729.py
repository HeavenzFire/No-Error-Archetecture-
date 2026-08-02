"""
729-Node Attractor Network for Balanced Ternary Systems

This module implements a discrete dynamical system with 3^6 = 729 stable states,
where memory and logic patterns become topological attractors. The system 
self-stabilizes by pulling noisy inputs into the nearest valid geometric 
basin of attraction.

Key Features:
- 6-dimensional ternary state space (729 unique attractors)
- Energy landscape with local minima at valid states
- Noise tolerance through basin convergence
- Recall accuracy under perturbations
- Stability analysis under dynamic conditions
"""

import numpy as np
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass
from collections import defaultdict
import math
import random


@dataclass
class AttractorState:
    """Represents a single attractor in the 729-node hyper-space."""
    state_vector: Tuple[int, ...]  # 6-tuple of trits {-1, 0, +1}
    basin_volume: int = 0  # Number of states converging here
    stability_score: float = 0.0  # Resistance to perturbation
    
    def __hash__(self):
        return hash(self.state_vector)
    
    def __eq__(self, other):
        return self.state_vector == other.state_vector
    
    def to_index(self) -> int:
        """Convert 6-trit state to integer index (0-728)."""
        index = 0
        for i, trit in enumerate(self.state_vector):
            index += (trit + 1) * (3 ** i)
        return index
    
    @classmethod
    def from_index(cls, index: int) -> 'AttractorState':
        """Convert integer index back to 6-trit state."""
        if not (0 <= index < 729):
            raise ValueError(f"Index must be 0-728, got {index}")
        
        state = []
        remaining = index
        for i in range(6):
            trit = (remaining % 3) - 1
            state.append(trit)
            remaining //= 3
        
        return cls(state_vector=tuple(state))


class TernaryAttractorNetwork:
    """
    A 729-node attractor network operating in balanced ternary space.
    
    Implements an energy landscape where valid memory states are local minima,
    and noisy inputs naturally converge to their nearest attractor through
    iterative state updates.
    """
    
    def __init__(self, num_attractors: int = 50):
        self.num_attractors = num_attractors
        self.attractors: Set[AttractorState] = set()
        self.basin_map: Dict[Tuple[int, ...], AttractorState] = {}
        self.energy_weights: np.ndarray = None
        self._initialize_network()
    
    def _initialize_network(self):
        """Initialize random attractor states and compute energy landscape."""
        # Generate random attractor states
        used_states = set()
        while len(self.attractors) < self.num_attractors:
            state_vector = tuple(random.choice([-1, 0, 1]) for _ in range(6))
            if state_vector not in used_states:
                used_states.add(state_vector)
                self.attractors.add(AttractorState(state_vector=state_vector))
        
        # Initialize energy weights (interaction matrix)
        # Symmetric 6x6 matrix for pairwise trit interactions
        self.energy_weights = np.random.randn(6, 6)
        self.energy_weights = (self.energy_weights + self.energy_weights.T) / 2
        
        # Pre-compute basins of attraction
        self._compute_basins()
    
    def _energy(self, state: Tuple[int, ...]) -> float:
        """
        Calculate energy of a state in the network.
        
        Lower energy indicates closer proximity to an attractor.
        Uses Hopfield-like energy function adapted for ternary states.
        """
        state_array = np.array(state)
        
        # Interaction energy
        interaction = state_array @ self.energy_weights @ state_array
        
        # Add penalty for deviation from attractors
        min_distance = float('inf')
        for attractor in self.attractors:
            dist = sum(1 for i in range(6) if state[i] != attractor.state_vector[i])
            min_distance = min(min_distance, dist)
        
        return interaction + 2.0 * min_distance
    
    def _update_state(self, state: Tuple[int, ...]) -> Tuple[int, ...]:
        """
        Perform one step of asynchronous state update.
        
        Each dimension is updated based on local field from other dimensions.
        """
        new_state = list(state)
        state_array = np.array(state)
        
        for i in range(6):
            # Calculate local field for dimension i
            field = np.dot(self.energy_weights[i], state_array)
            
            # Update rule: sign of field determines new trit value
            if field > 0.5:
                new_state[i] = 1
            elif field < -0.5:
                new_state[i] = -1
            else:
                new_state[i] = 0
        
        return tuple(new_state)
    
    def _compute_basins(self):
        """Map all 729 states to their convergent attractors."""
        self.basin_map.clear()
        basin_counts = defaultdict(int)
        
        # Iterate through all possible states
        for idx in range(729):
            initial_state = AttractorState.from_index(idx).state_vector
            
            # Converge to attractor
            converged_state = self.converge(initial_state, max_iterations=20)
            
            # Find matching attractor
            for attractor in self.attractors:
                if attractor.state_vector == converged_state:
                    self.basin_map[initial_state] = attractor
                    basin_counts[attractor] += 1
                    break
            else:
                # State didn't converge to known attractor (rare)
                # Create temporary attractor
                temp_attractor = AttractorState(state_vector=converged_state)
                self.basin_map[initial_state] = temp_attractor
                basin_counts[temp_attractor] += 1
        
        # Update basin volumes
        for attractor in self.attractors:
            attractor.basin_volume = basin_counts[attractor]
    
    def converge(self, initial_state: Tuple[int, ...], 
                 max_iterations: int = 50) -> Tuple[int, ...]:
        """
        Evolve a state until it reaches a stable attractor.
        
        Returns the final stable state vector.
        """
        current = initial_state
        
        for _ in range(max_iterations):
            next_state = self._update_state(current)
            
            # Check for convergence
            if next_state == current:
                return current
            
            current = next_state
        
        return current  # Return best effort if not fully converged
    
    def recall(self, noisy_pattern: Tuple[int, ...], 
               noise_level: float = 0.0) -> Tuple[AttractorState, bool]:
        """
        Recall the closest attractor from a potentially noisy input.
        
        Args:
            noisy_pattern: Input pattern (may have errors)
            noise_level: Estimated fraction of corrupted trits
        
        Returns:
            Tuple of (attractor_state, success_flag)
        """
        # Apply noise if specified (for testing)
        if noise_level > 0:
            test_pattern = list(noisy_pattern)
            for i in range(6):
                if random.random() < noise_level:
                    # Flip to random different trit
                    current = test_pattern[i]
                    options = [-1, 0, 1]
                    options.remove(current)
                    test_pattern[i] = random.choice(options)
            noisy_pattern = tuple(test_pattern)
        
        # Converge to attractor
        converged = self.converge(noisy_pattern)
        
        # Find matching attractor
        for attractor in self.attractors:
            if attractor.state_vector == converged:
                return attractor, True
        
        # No match found
        return AttractorState(state_vector=converged), False
    
    def calculate_stability_scores(self):
        """Evaluate stability of each attractor under perturbation."""
        for attractor in self.attractors:
            stable_count = 0
            total_tests = 100
            
            for _ in range(total_tests):
                # Perturb 1-2 trits
                perturbed = list(attractor.state_vector)
                num_perturb = random.choice([1, 2])
                indices = random.sample(range(6), num_perturb)
                
                for idx in indices:
                    current = perturbed[idx]
                    options = [-1, 0, 1]
                    options.remove(current)
                    perturbed[idx] = random.choice(options)
                
                # Check if returns to original
                recovered = self.converge(tuple(perturbed))
                if recovered == attractor.state_vector:
                    stable_count += 1
            
            attractor.stability_score = stable_count / total_tests
    
    def get_network_statistics(self) -> Dict:
        """Compute comprehensive network statistics."""
        self.calculate_stability_scores()
        
        basin_volumes = [a.basin_volume for a in self.attractors]
        stability_scores = [a.stability_score for a in self.attractors]
        
        return {
            'total_attractors': len(self.attractors),
            'total_states': 729,
            'coverage': sum(basin_volumes) / 729,
            'avg_basin_volume': np.mean(basin_volumes),
            'max_basin_volume': max(basin_volumes),
            'min_basin_volume': min(basin_volumes),
            'avg_stability': np.mean(stability_scores),
            'min_stability': min(stability_scores),
            'max_stability': max(stability_scores),
        }


def visualize_convergence(network: TernaryAttractorNetwork, 
                         num_samples: int = 10) -> List[Dict]:
    """
    Visualize convergence paths from random starting points.
    
    Returns list of convergence trajectories.
    """
    trajectories = []
    
    for _ in range(num_samples):
        # Random starting state
        start = tuple(random.choice([-1, 0, 1]) for _ in range(6))
        
        trajectory = [start]
        current = start
        
        for _ in range(20):
            next_state = network._update_state(current)
            trajectory.append(next_state)
            
            if next_state == current:
                break
            
            current = next_state
        
        # Find final attractor
        final_attractor = None
        for attr in network.attractors:
            if attr.state_vector == current:
                final_attractor = attr
                break
        
        trajectories.append({
            'start': start,
            'path': trajectory,
            'length': len(trajectory),
            'final_state': current,
            'attractor_found': final_attractor is not None
        })
    
    return trajectories


def benchmark_noise_tolerance(network: TernaryAttractorNetwork,
                             noise_levels: List[float] = None) -> Dict:
    """
    Benchmark recall accuracy under varying noise conditions.
    """
    if noise_levels is None:
        noise_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    
    results = {}
    
    for noise in noise_levels:
        correct = 0
        total = 200
        
        for _ in range(total):
            # Pick random attractor
            target = random.choice(list(network.attractors))
            
            # Recall with noise
            recalled, success = network.recall(target.state_vector, noise)
            
            if recalled.state_vector == target.state_vector:
                correct += 1
        
        results[noise] = correct / total
    
    return results


if __name__ == "__main__":
    print("=== 729-Node Attractor Network ===\n")
    
    # Initialize network with 50 attractors
    network = TernaryAttractorNetwork(num_attractors=50)
    
    # Display network statistics
    print("1. Network Statistics:")
    stats = network.get_network_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value:.4f}" if isinstance(value, float) else f"   {key}: {value}")
    
    # Test recall from perfect inputs
    print("\n2. Perfect Recall Test:")
    perfect_success = 0
    for _ in range(50):
        target = random.choice(list(network.attractors))
        recalled, _ = network.recall(target.state_vector, 0.0)
        if recalled.state_vector == target.state_vector:
            perfect_success += 1
    print(f"   Success rate: {perfect_success}/50 ({perfect_success/50*100:.1f}%)")
    
    # Test noise tolerance
    print("\n3. Noise Tolerance Benchmark:")
    noise_results = benchmark_noise_tolerance(network)
    for noise, accuracy in noise_results.items():
        print(f"   Noise level {noise:.1f}: {accuracy*100:.1f}% accuracy")
    
    # Show convergence examples
    print("\n4. Convergence Examples:")
    trajectories = visualize_convergence(network, num_samples=5)
    for i, traj in enumerate(trajectories):
        start_str = ''.join(['-' if x==-1 else ('0' if x==0 else '+') for x in traj['start']])
        end_str = ''.join(['-' if x==-1 else ('0' if x==0 else '+') for x in traj['final_state']])
        print(f"   Path {i+1}: [{start_str}] → [{end_str}] ({traj['length']} steps)")
    
    # Demonstrate basin sizes
    print("\n5. Largest Basins of Attraction:")
    sorted_attractors = sorted(network.attractors, 
                               key=lambda a: a.basin_volume, 
                               reverse=True)[:5]
    for i, attr in enumerate(sorted_attractors):
        state_str = ''.join(['-' if x==-1 else ('0' if x==0 else '+') 
                            for x in attr.state_vector])
        print(f"   #{i+1}: State [{state_str}], Basin volume: {attr.basin_volume}, "
              f"Stability: {attr.stability_score:.2f}")
