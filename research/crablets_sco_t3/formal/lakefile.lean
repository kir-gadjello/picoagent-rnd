import Lake
open Lake DSL

package ScoT3 where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.28.0"

@[default_target]
lean_lib ScoT3 where
  globs := #[`ScoT3]
