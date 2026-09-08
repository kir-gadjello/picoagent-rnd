import ScoT3.Core
import ScoT3.Online

namespace ScoT3

/-- Projection used by a learned scalar gate. Keeping the admissible gate in
`[0,1]` makes composition remain a convex mixture and therefore preserves the
local boundedness contract proved in `Core`. This real-valued mathematical model
is intentionally noncomputable; executable floating-point refinement is a
separate implementation theorem. -/
noncomputable def clip01 (x : ℝ) : ℝ :=
  if x < 0 then 0 else if 1 < x then 1 else x

/-- Projection is always a legal convex-mixture coefficient. -/
theorem clip01_bounds (x : ℝ) : 0 ≤ clip01 x ∧ clip01 x ≤ 1 := by
  by_cases h0 : x < 0
  · simp [clip01, h0]
  · have hx0 : 0 ≤ x := le_of_not_gt h0
    by_cases h1 : 1 < x
    · simp [clip01, h0, h1]
    · have hx1 : x ≤ 1 := le_of_not_gt h1
      simp [clip01, h0, h1, hx0, hx1]

/-- Scalar projection onto `[0,1]` cannot increase squared distance to a legal
comparator. This is the exact proof obligation needed by projected local gate
learning; no recurrent history appears in the statement. -/
theorem clip01_sq_dist_le (x u : ℝ) (hu0 : 0 ≤ u) (hu1 : u ≤ 1) :
    (clip01 x - u)^2 ≤ (x-u)^2 := by
  by_cases h0 : x < 0
  · have hxu : x * u ≤ 0 := mul_nonpos_of_nonpos_of_nonneg (le_of_lt h0) hu0
    simp [clip01, h0]
    nlinarith [sq_nonneg x]
  · have hx0 : 0 ≤ x := le_of_not_gt h0
    by_cases h1 : 1 < x
    · have hxm : 0 ≤ x - 1 := by linarith
      have hsum : 0 ≤ x + 1 - 2*u := by linarith
      have hprod : 0 ≤ (x-1) * (x+1-2*u) := mul_nonneg hxm hsum
      simp [clip01, h0, h1]
      nlinarith
    · have hx1 : x ≤ 1 := le_of_not_gt h1
      simp [clip01, h0, h1]

/-- One local projected-gradient step for a scalar routing gate. -/
noncomputable def projectedGateStep (η g a : ℝ) : ℝ := clip01 (ogdStep η g a)

/-- Projected local learning inherits the usual OGD potential upper bound. -/
theorem projectedGate_potential_le (η g a u : ℝ)
    (hu0 : 0 ≤ u) (hu1 : u ≤ 1) :
    (projectedGateStep η g a-u)^2 ≤
      (a-u)^2 - 2*η*g*(a-u) + η^2*g^2 := by
  have hp := clip01_sq_dist_le (ogdStep η g a) u hu0 hu1
  rw [ogd_potential_identity] at hp
  exact hp

/-- Squared loss of a local convex mixture between two child predictions. -/
def mixSqLoss (p q y a : ℝ) : ℝ := (mix a p q-y)^2

/-- Exact derivative with respect to the local gate only. -/
def mixSqGrad (p q y a : ℝ) : ℝ := 2*(q-p)*(mix a p q-y)

/-- The local gate objective is convex in its own scalar coefficient. Thus a gate
can be trained against its two child predictions without differentiating through
either child or through earlier recurrent time steps. -/
theorem mixSqLoss_firstOrder (p q y a u : ℝ) :
    mixSqLoss p q y a - mixSqLoss p q y u ≤ mixSqGrad p q y a * (a-u) := by
  simp [mixSqLoss, mixSqGrad, mix]
  nlinarith [sq_nonneg ((q-p)*(a-u))]

/-- One-step deterministic regret conversion for the learned local mixture gate.
The comparator is any fixed legal mixture coefficient in `[0,1]`. -/
theorem projectedGate_one_step_regret
    (η p q y a u : ℝ)
    (hη : 0 ≤ η) (hu0 : 0 ≤ u) (hu1 : u ≤ 1) :
    2*η*(mixSqLoss p q y a - mixSqLoss p q y u) ≤
      (a-u)^2 -
        (projectedGateStep η (mixSqGrad p q y a) a-u)^2 +
        η^2*(mixSqGrad p q y a)^2 := by
  have hfo := mixSqLoss_firstOrder p q y a u
  have hpot := projectedGate_potential_le η (mixSqGrad p q y a) a u hu0 hu1
  have hmul :
      2*η*(mixSqLoss p q y a - mixSqLoss p q y u) ≤
        2*η*(mixSqGrad p q y a*(a-u)) := by
    exact mul_le_mul_of_nonneg_left hfo (mul_nonneg (by norm_num) hη)
  nlinarith

#print axioms clip01_sq_dist_le
#print axioms projectedGate_potential_le
#print axioms mixSqLoss_firstOrder
#print axioms projectedGate_one_step_regret

end ScoT3
