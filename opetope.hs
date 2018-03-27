{-# LANGUAGE DataKinds, KindSignatures, GADTs, StandaloneDeriving, FlexibleInstances #-}

module BSC where
  import Data.List

  data Nat = Zero | S Nat deriving Show

  data Opetope :: Nat -> * where
    Point :: Opetope Zero
    Opt :: [(Opetope n)] -> Opetope n -> Opetope (S n)

  instance Show (Opetope Zero) where
    show s = "s"

  instance Show (Opetope (S n)) where
    show s = "g"
  