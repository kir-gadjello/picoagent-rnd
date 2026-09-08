import Mathlib

namespace ScoT3

/-- Probability assigned to a Boolean observation. -/
def bitProb (p : ℝ) (b : Bool) : ℝ := if b then p else 1-p

/-- Prequential binary log loss in nats. -/
def bitLogLoss (p : ℝ) (b : Bool) : ℝ := -Real.log (bitProb p b)

/-- Joint probability assigned by a sequence of one-step predictors. -/
def seqProb {n : ℕ} (p : Fin n → ℝ) (b : Fin n → Bool) : ℝ :=
  ∏ i, bitProb (p i) (b i)

/-- Cumulative prequential log loss. -/
def seqLogLoss {n : ℕ} (p : Fin n → ℝ) (b : Fin n → Bool) : ℝ :=
  ∑ i, bitLogLoss (p i) (b i)

/-- Cumulative log loss is exactly negative log joint predictive probability when
all assigned observation probabilities are nonzero. This is the formal bridge
from an online prediction oracle to prequential codelength. -/
theorem seqLogLoss_eq_neg_log_seqProb {n : ℕ}
    (p : Fin n → ℝ) (b : Fin n → Bool)
    (h : ∀ i, bitProb (p i) (b i) ≠ 0) :
    seqLogLoss p b = -Real.log (seqProb p b) := by
  simp [seqLogLoss, bitLogLoss, seqProb, Real.log_prod h]

/-- A perfect deterministic prediction costs zero nats. -/
theorem deterministic_bit_zero_loss (b : Bool) :
    bitLogLoss (if b then 1 else 0) b = 0 := by
  cases b <;> simp [bitLogLoss, bitProb]

#print axioms seqLogLoss_eq_neg_log_seqProb
#print axioms deterministic_bit_zero_loss

end ScoT3
