import Mathlib
import ScoT3.Codelength

namespace ScoT3

/-- Krichevsky–Trofimov/Beta(1/2,1/2) reliability used to calibrate a
binary expert from local match/mismatch counts. -/
def ktReliability (matches mismatches : ℝ) : ℝ :=
  (matches + (1/2 : ℝ)) / (matches + mismatches + 1)

/-- With nonnegative counts the KT reliability is a strict probability. -/
theorem ktReliability_mem_openUnit (matches mismatches : ℝ)
    (hm : 0 ≤ matches) (he : 0 ≤ mismatches) :
    0 < ktReliability matches mismatches ∧ ktReliability matches mismatches < 1 := by
  have hnum : 0 < matches + (1/2 : ℝ) := by linarith
  have hden : 0 < matches + mismatches + 1 := by linarith
  constructor
  · exact div_pos hnum hden
  · apply (div_lt_one hden).2
    linarith

/-- Turn a raw Boolean expert output and a reliability probability into a
calibrated Bernoulli probability. -/
def calibratedBitProb (reliability : ℝ) (raw : Bool) : ℝ :=
  if raw then reliability else 1-reliability

/-- Calibration preserves the probability interval. -/
theorem calibratedBitProb_bounds (r : ℝ) (raw : Bool)
    (hr0 : 0 ≤ r) (hr1 : r ≤ 1) :
    0 ≤ calibratedBitProb r raw ∧ calibratedBitProb r raw ≤ 1 := by
  cases raw <;> simp [calibratedBitProb] <;> constructor <;> linarith

/-- Exponential-weight routing never destroys a positive expert weight. -/
noncomputable def hedgeWeight (η loss weight : ℝ) : ℝ :=
  weight * Real.exp (-η*loss)

theorem hedgeWeight_pos (η loss weight : ℝ) (hw : 0 < weight) :
    0 < hedgeWeight η loss weight := by
  exact mul_pos hw (Real.exp_pos _)

/-- A normalized nonnegative finite-expert mixture of probabilities is itself a
probability. This is the compositional safety theorem used by finite routing
layers independent of how the weights were learned. -/
theorem finiteExpertMixture_bounds {ι : Type*} [Fintype ι]
    (w p : ι → ℝ)
    (hw : ∀ i, 0 ≤ w i)
    (hsum : ∑ i, w i = 1)
    (hp0 : ∀ i, 0 ≤ p i)
    (hp1 : ∀ i, p i ≤ 1) :
    0 ≤ ∑ i, w i * p i ∧ (∑ i, w i * p i) ≤ 1 := by
  constructor
  · exact Finset.sum_nonneg (fun i _ => mul_nonneg (hw i) (hp0 i))
  · calc
      (∑ i, w i * p i) ≤ ∑ i, w i * 1 := by
        exact Finset.sum_le_sum (fun i _ => mul_le_mul_of_nonneg_left (hp1 i) (hw i))
      _ = 1 := by simpa using hsum

/-- Exact decoder/encoder pairs force a finite state-space cardinality lower
bound: exact memory cannot be obtained for free by making the fading carrier
more contractive. -/
theorem exact_recall_card_le {Message State : Type*}
    [Fintype Message] [Fintype State]
    (encode : Message → State) (decode : State → Message)
    (h : ∀ m, decode (encode m) = m) :
    Fintype.card Message ≤ Fintype.card State := by
  exact Fintype.card_le_of_injective encode (exact_recall_injective encode decode h)

#print axioms ktReliability_mem_openUnit
#print axioms calibratedBitProb_bounds
#print axioms hedgeWeight_pos
#print axioms finiteExpertMixture_bounds
#print axioms exact_recall_card_le

end ScoT3
