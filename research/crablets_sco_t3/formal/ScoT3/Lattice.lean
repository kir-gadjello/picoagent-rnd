import ScoT3.Core

namespace ScoT3

/-- Additive energy certificate for a finite heterogeneous tile lattice. -/
def latticeEnergy {ι X : Type*} [Fintype ι]
    (E : ι → X → ℝ) (x : ι → X) : ℝ :=
  ∑ i, E i (x i)

/-- Parallel local update of a finite lattice of proof-carrying passive tiles. -/
def latticeStep {ι X : Type*} [Fintype ι]
    (E : ι → X → ℝ) (tile : ∀ i, Passive X (E i))
    (x : ι → X) : ι → X :=
  fun i => (tile i).step (x i)

/-- Local pointwise passivity scales to any finite heterogeneous lattice by
summation; no global Jacobian or reverse-time argument is required. -/
theorem lattice_energy_noninc {ι X : Type*} [Fintype ι]
    (E : ι → X → ℝ) (tile : ∀ i, Passive X (E i))
    (x : ι → X) :
    latticeEnergy E (latticeStep E tile x) ≤ latticeEnergy E x := by
  apply Finset.sum_le_sum
  intro i hi
  exact (tile i).noninc (x i)

/-- Package the whole finite lattice back into the same compositional passive
interface. This is the key proof-carrying scaling seam. -/
def latticePassive {ι X : Type*} [Fintype ι]
    (E : ι → X → ℝ) (tile : ∀ i, Passive X (E i)) :
    Passive (ι → X) (latticeEnergy E) where
  step := latticeStep E tile
  noninc := lattice_energy_noninc E tile

/-- Even if the certified tile primitive chosen at each site changes at every
step, finite-horizon lattice energy remains bounded by the initial energy. -/
theorem switched_lattice_passive {ι X : Type*} [Fintype ι]
    (E : ι → X → ℝ) (tile : ℕ → ∀ i, Passive X (E i))
    (x : ι → X) : ∀ n,
    latticeEnergy E
      (evolve (fun t => latticeStep E (tile t)) x n) ≤ latticeEnergy E x := by
  exact switched_passive (latticeEnergy E)
    (fun t => latticeStep E (tile t))
    (fun t z => lattice_energy_noninc E (tile t) z) x

#print axioms lattice_energy_noninc
#print axioms switched_lattice_passive

end ScoT3
