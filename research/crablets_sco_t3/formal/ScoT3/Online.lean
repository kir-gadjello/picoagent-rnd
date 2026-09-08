import Mathlib

namespace ScoT3

/-- One scalar online-gradient step. This is deliberately local: it does not
backpropagate through recurrent history. -/
def ogdStep (η g w : ℝ) : ℝ := w - η*g

/-- Exact potential identity underlying the regret proof. -/
theorem ogd_potential_identity (η g w u : ℝ) :
    (ogdStep η g w - u)^2 =
      (w-u)^2 - 2*η*g*(w-u) + η^2*g^2 := by
  simp [ogdStep]
  ring

/-- Any loss exposing a valid first-order upper bound can use the same local
online-learning proof spine. -/
def FirstOrderContract (loss grad : ℝ → ℝ) : Prop :=
  ∀ w u, loss w - loss u ≤ grad w * (w-u)

/-- One-step regret-to-potential conversion. -/
theorem ogd_one_step_regret (η g w u r : ℝ)
    (hη : 0 ≤ η) (hr : r ≤ g*(w-u)) :
    2*η*r ≤ (w-u)^2 - (ogdStep η g w-u)^2 + η^2*g^2 := by
  calc
    2*η*r ≤ 2*η*(g*(w-u)) := by
      exact mul_le_mul_of_nonneg_left hr (mul_nonneg (by norm_num) hη)
    _ = (w-u)^2 - (ogdStep η g w-u)^2 + η^2*g^2 := by
      rw [ogd_potential_identity]
      ring

/-- Squared loss of a scalar linear readout. -/
def sqLoss (x y w : ℝ) : ℝ := (w*x-y)^2

/-- Its exact local gradient. -/
def sqGrad (x y w : ℝ) : ℝ := 2*x*(w*x-y)

/-- Squared linear loss satisfies the first-order convexity inequality by a
pure polynomial argument. -/
theorem sqLoss_firstOrder (x y w u : ℝ) :
    sqLoss x y w - sqLoss x y u ≤ sqGrad x y w * (w-u) := by
  simp [sqLoss, sqGrad]
  nlinarith [sq_nonneg (x*(w-u))]

/-- Online iterate for a time-varying sequence of local loss gradients. -/
def ogdSeq (η : ℝ) (grad : ℕ → ℝ → ℝ) (w₀ : ℝ) : ℕ → ℝ
  | 0 => w₀
  | n + 1 => ogdStep η (grad n (ogdSeq η grad w₀ n)) (ogdSeq η grad w₀ n)

/-- Deterministic adversarial regret telescope. No stochastic assumption and no
reverse-time pass are hidden in the statement. -/
theorem ogd_regret_telescope
    (η : ℝ) (hη : 0 ≤ η)
    (loss grad : ℕ → ℝ → ℝ)
    (hfirst : ∀ t w u, loss t w - loss t u ≤ grad t w * (w-u))
    (w₀ u : ℝ) : ∀ T,
    let w := ogdSeq η grad w₀
    2*η*(∑ t ∈ Finset.range T, (loss t (w t) - loss t u)) ≤
      (w₀-u)^2 - (w T-u)^2 +
        η^2*(∑ t ∈ Finset.range T, (grad t (w t))^2) := by
  intro T
  induction T with
  | zero => simp
  | succ T ih =>
      let w := ogdSeq η grad w₀
      have hstep := ogd_one_step_regret η (grad T (w T)) (w T) u
        (loss T (w T) - loss T u) hη (hfirst T (w T) u)
      change 2*η*(∑ t ∈ Finset.range (T+1), (loss t (w t) - loss t u)) ≤ _
      simp only [Finset.sum_range_succ]
      have hw : w (T+1) = ogdStep η (grad T (w T)) (w T) := rfl
      rw [hw]
      nlinarith

/-- Dropping the nonnegative final potential yields the conventional regret upper
bound. -/
theorem ogd_regret_bound
    (η : ℝ) (hη : 0 ≤ η)
    (loss grad : ℕ → ℝ → ℝ)
    (hfirst : ∀ t w u, loss t w - loss t u ≤ grad t w * (w-u))
    (w₀ u : ℝ) (T : ℕ) :
    let w := ogdSeq η grad w₀
    2*η*(∑ t ∈ Finset.range T, (loss t (w t) - loss t u)) ≤
      (w₀-u)^2 + η^2*(∑ t ∈ Finset.range T, (grad t (w t))^2) := by
  have h := ogd_regret_telescope η hη loss grad hfirst w₀ u T
  dsimp at h ⊢
  nlinarith [sq_nonneg (ogdSeq η grad w₀ T-u)]

#print axioms sqLoss_firstOrder
#print axioms ogd_regret_telescope
#print axioms ogd_regret_bound

end ScoT3
