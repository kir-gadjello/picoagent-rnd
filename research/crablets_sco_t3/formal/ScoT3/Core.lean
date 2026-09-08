import Mathlib

namespace ScoT3

/-- A proof-carrying passive state transition. The operator grammar is deliberately
small: every carrier primitive must provide a pointwise energy certificate. -/
structure Passive (X : Type*) (E : X → ℝ) where
  step : X → X
  noninc : ∀ x, E (step x) ≤ E x

namespace Passive

/-- Certified passive maps compose without reopening their internals. -/
def comp {X : Type*} {E : X → ℝ} (a b : Passive X E) : Passive X E where
  step := fun x => b.step (a.step x)
  noninc := fun x => le_trans (b.noninc (a.step x)) (a.noninc x)

/-- State-dependent discrete control is safe when every branch is already certified. -/
def choose {X : Type*} {E : X → ℝ} (gate : X → Bool)
    (a b : Passive X E) : Passive X E where
  step := fun x => if gate x then a.step x else b.step x
  noninc := by
    intro x
    cases h : gate x <;> simp [h, a.noninc, b.noninc]

end Passive

/-- Evolution under an arbitrary time-varying family of transitions. -/
def evolve {X : Type*} (f : ℕ → X → X) (x : X) : ℕ → X
  | 0 => x
  | n + 1 => f n (evolve f x n)

/-- Pointwise passivity is enough for arbitrary finite switching schedules. -/
theorem switched_passive {X : Type*} (E : X → ℝ) (f : ℕ → X → X)
    (h : ∀ n x, E (f n x) ≤ E x) (x : X) :
    ∀ n, E (evolve f x n) ≤ E x := by
  intro n
  induction n with
  | zero => exact le_rfl
  | succ n ih => exact le_trans (h n (evolve f x n)) ih

/-- Concrete two-channel real Givens primitive. -/
def givens (c s x y : ℝ) : ℝ × ℝ := (c*x - s*y, s*x + c*y)

/-- The carrier's primitive conservation law. -/
theorem givens_energy (c s x y : ℝ) (hcs : c^2 + s^2 = 1) :
    (givens c s x y).1^2 + (givens c s x y).2^2 = x^2 + y^2 := by
  simp [givens]
  nlinarith [sq_nonneg (c*x - s*y), sq_nonneg (s*x + c*y)]

/-- Explicit cavity semantics: persistence is a separate state contract, not a
near-unit pole hidden in the passive carrier. -/
def cavityStep {α : Type*} (write : Bool) (old fresh : α) : α :=
  if write then fresh else old

@[simp] theorem cavity_hold {α : Type*} (old fresh : α) :
    cavityStep false old fresh = old := rfl

@[simp] theorem cavity_write {α : Type*} (old fresh : α) :
    cavityStep true old fresh = fresh := rfl

/-- A convex scalar gate. In implementation the gate can be learned locally; in
proofs it is explicitly charged as a bounded control variable. -/
def mix (a x y : ℝ) : ℝ := (1-a)*x + a*y

/-- Convex mixing cannot leave a shared interval [-B,B]. -/
theorem mix_abs_le (a x y B : ℝ)
    (ha0 : 0 ≤ a) (ha1 : a ≤ 1)
    (hx : |x| ≤ B) (hy : |y| ≤ B) : |mix a x y| ≤ B := by
  have h1a : 0 ≤ 1-a := sub_nonneg.mpr ha1
  calc
    |mix a x y| ≤ |(1-a)*x| + |a*y| := by
      simpa [mix] using abs_add ((1-a)*x) (a*y)
    _ = (1-a)*|x| + a*|y| := by
      rw [abs_mul, abs_mul, abs_of_nonneg h1a, abs_of_nonneg ha0]
    _ ≤ (1-a)*B + a*B := by
      exact add_le_add (mul_le_mul_of_nonneg_left hx h1a)
        (mul_le_mul_of_nonneg_left hy ha0)
    _ = B := by ring

/-- Exact recall requires an injective encoder, exposing finite-state memory cost. -/
theorem exact_recall_injective {Message State : Type*}
    (encode : Message → State) (decode : State → Message)
    (h : ∀ m, decode (encode m) = m) : Function.Injective encode := by
  intro a b hab
  calc
    a = decode (encode a) := (h a).symm
    _ = decode (encode b) := congrArg decode hab
    _ = b := h b

/-- A strict contraction cannot hold two separated exact fixed memories. -/
theorem strict_contraction_no_two_fixed (d q : ℝ) (hd : 0 < d) (hq : q < 1) :
    ¬ d ≤ q*d := by
  intro h
  nlinarith [mul_pos (sub_pos.mpr hq) hd]

#print axioms switched_passive
#print axioms givens_energy
#print axioms mix_abs_le
#print axioms exact_recall_injective

end ScoT3
