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

/-- Uniform Bayesian mixture likelihood over a finite expert class. -/
noncomputable def uniformLikelihoodMixture {ι : Type*} [Fintype ι]
    (likelihood : ι → ℝ) : ℝ :=
  (∑ i, likelihood i) / (Fintype.card ι : ℝ)

/-- A uniform finite mixture pays at most `log N` extra nats relative to any
single positive expert likelihood. This is the proof-centric reason to use
Bayesian/log-loss routing for finite delay experts. -/
theorem uniformLikelihoodMixture_codelength_le {ι : Type*} [Fintype ι]
    (likelihood : ι → ℝ) (j : ι)
    (hpos : ∀ i, 0 < likelihood i)
    (hcard : 0 < (Fintype.card ι : ℝ)) :
    -Real.log (uniformLikelihoodMixture likelihood) ≤
      -Real.log (likelihood j) + Real.log (Fintype.card ι : ℝ) := by
  have hsum : likelihood j ≤ ∑ i, likelihood i := by
    exact Finset.single_le_sum (fun i _ => le_of_lt (hpos i)) (Finset.mem_univ j)
  have hsumpos : 0 < ∑ i, likelihood i := lt_of_lt_of_le (hpos j) hsum
  have hmixpos : 0 < uniformLikelihoodMixture likelihood := by
    exact div_pos hsumpos hcard
  have hjdiv : 0 < likelihood j / (Fintype.card ι : ℝ) := div_pos (hpos j) hcard
  have hdom : likelihood j / (Fintype.card ι : ℝ) ≤ uniformLikelihoodMixture likelihood := by
    exact div_le_div_of_nonneg_right hsum (le_of_lt hcard)
  have hlog :
      Real.log (likelihood j / (Fintype.card ι : ℝ)) ≤
        Real.log (uniformLikelihoodMixture likelihood) :=
    (Real.log_le_log hjdiv hmixpos).2 hdom
  rw [Real.log_div (ne_of_gt (hpos j)) (ne_of_gt hcard)] at hlog
  linarith

/-- Bayesian multiplicative updating has the exact total-mass identity behind
prequential mixture coding. -/
theorem bayes_total_mass_step {ι : Type*} [Fintype ι]
    (weight obsProb : ι → ℝ) (hW : (∑ i, weight i) ≠ 0) :
    (∑ i, weight i * obsProb i) =
      ((∑ i, weight i * obsProb i) / (∑ i, weight i)) * (∑ i, weight i) := by
  field_simp

/-- General prior-weighted likelihood mixture. Hidden-state paths of a finite
fixed-share router are just another finite expert class under this definition. -/
noncomputable def weightedLikelihoodMixture {ι : Type*} [Fintype ι]
    (prior likelihood : ι → ℝ) : ℝ :=
  ∑ i, prior i * likelihood i

/-- Any positive path/expert in a finite prior-weighted mixture gives a direct
codelength upper bound: mixture code length is at most that expert's code length
plus the negative log prior of the path. This is the formal tracking contract
needed by a fixed-share HMM router once its transition prior is instantiated. -/
theorem weightedLikelihoodMixture_codelength_le {ι : Type*} [Fintype ι]
    (prior likelihood : ι → ℝ) (j : ι)
    (hprior : ∀ i, 0 ≤ prior i)
    (hpriorj : 0 < prior j)
    (hlike : ∀ i, 0 < likelihood i) :
    -Real.log (weightedLikelihoodMixture prior likelihood) ≤
      -Real.log (likelihood j) - Real.log (prior j) := by
  have htermpos : 0 < prior j * likelihood j := mul_pos hpriorj (hlike j)
  have hsum : prior j * likelihood j ≤ weightedLikelihoodMixture prior likelihood := by
    exact Finset.single_le_sum
      (fun i _ => mul_nonneg (hprior i) (le_of_lt (hlike i))) (Finset.mem_univ j)
  have hmixpos : 0 < weightedLikelihoodMixture prior likelihood := lt_of_lt_of_le htermpos hsum
  have hlog : Real.log (prior j * likelihood j) ≤
      Real.log (weightedLikelihoodMixture prior likelihood) :=
    (Real.log_le_log htermpos hmixpos).2 hsum
  rw [Real.log_mul (ne_of_gt hpriorj) (ne_of_gt (hlike j))] at hlog
  linarith

/-- One coordinate of the fixed-share transition. `share/card` is explicit
probability mass reserved for recovery from a stale routing hypothesis. -/
def fixedShareMass (share card p : ℝ) : ℝ := (1-share)*p + share/card

/-- With a legal share and nonnegative incoming mass, every coordinate receives
at least the uniform share floor. This is the local reason a new lag can recover
after a nonstationary switch instead of having vanishing posterior support. -/
theorem fixedShareMass_floor (share card p : ℝ)
    (hs0 : 0 ≤ share) (hs1 : share ≤ 1) (hc : 0 < card) (hp : 0 ≤ p) :
    share/card ≤ fixedShareMass share card p := by
  have h1s : 0 ≤ 1-share := sub_nonneg.mpr hs1
  have hprod : 0 ≤ (1-share)*p := mul_nonneg h1s hp
  simp [fixedShareMass]
  linarith

#print axioms ktReliability_mem_openUnit
#print axioms calibratedBitProb_bounds
#print axioms hedgeWeight_pos
#print axioms finiteExpertMixture_bounds
#print axioms exact_recall_card_le
#print axioms uniformLikelihoodMixture_codelength_le
#print axioms bayes_total_mass_step
#print axioms weightedLikelihoodMixture_codelength_le
#print axioms fixedShareMass_floor

end ScoT3
