import Mathlib

namespace ScoT3

/-- Probability assigned to a Boolean observation. -/
def bitProb (p : ℝ) (b : Bool) : ℝ := if b then p else 1-p

/-- Prequential binary log loss in nats. -/
noncomputable def bitLogLoss (p : ℝ) (b : Bool) : ℝ := -Real.log (bitProb p b)

/-- Joint probability assigned by a sequence of one-step predictors. -/
def seqProb {n : ℕ} (p : Fin n → ℝ) (b : Fin n → Bool) : ℝ :=
  ∏ i, bitProb (p i) (b i)

/-- Cumulative prequential log loss. -/
noncomputable def seqLogLoss {n : ℕ} (p : Fin n → ℝ) (b : Fin n → Bool) : ℝ :=
  ∑ i, bitLogLoss (p i) (b i)

/-- Cumulative log loss is exactly negative log joint predictive probability when
all assigned observation probabilities are nonzero. This is the formal bridge
from an online prediction oracle to prequential codelength. -/
theorem seqLogLoss_eq_neg_log_seqProb {n : ℕ}
    (p : Fin n → ℝ) (b : Fin n → Bool)
    (h : ∀ i, bitProb (p i) (b i) ≠ 0) :
    seqLogLoss p b = -Real.log (seqProb p b) := by
  have hlog :
      Real.log (∏ i : Fin n, bitProb (p i) (b i)) =
        ∑ i : Fin n, Real.log (bitProb (p i) (b i)) := by
    simpa using (Real.log_prod (s := Finset.univ)
      (f := fun i : Fin n => bitProb (p i) (b i)) (fun i _ => h i))
  calc
    seqLogLoss p b = -(∑ i : Fin n, Real.log (bitProb (p i) (b i))) := by
      simp [seqLogLoss, bitLogLoss]
    _ = -Real.log (seqProb p b) := by
      simpa [seqProb] using congrArg Neg.neg hlog.symm

/-- A perfect deterministic prediction costs zero nats. -/
theorem deterministic_bit_zero_loss (b : Bool) :
    bitLogLoss (if b then 1 else 0) b = 0 := by
  cases b <;> simp [bitLogLoss, bitProb]

#print axioms seqLogLoss_eq_neg_log_seqProb
#print axioms deterministic_bit_zero_loss

end ScoT3
