import Mathlib

noncomputable section

namespace PovertyPPP

inductive MoneyUnit where
  /-- Indian rupees -/
  | rupee
  /-- PPP dollars where US prices are in this unit as the base country -/
  | ppp

@[ext]
structure Money (u : MoneyUnit) where
  val : ℝ

instance {u : MoneyUnit} : LT (Money u) := ⟨fun a b => a.val < b.val⟩

instance {u : MoneyUnit} : LE (Money u) := ⟨fun a b => a.val ≤ b.val⟩

@[simp]
theorem Money.lt_def {u : MoneyUnit} (a b : Money u) : a < b ↔ a.val < b.val := Iff.rfl

/-- Units of `a` per unit of `b` -/
structure Rate (a b : MoneyUnit) where
  val : ℝ

def convert {a b : MoneyUnit} (r : Rate a b) (m : Money b) : Money a :=
  ⟨r.val * m.val⟩

@[simp]
theorem convert_val {a b : MoneyUnit} (r : Rate a b) (m : Money b) :
  (convert r m).val = r.val * m.val := rfl

structure Prices (u : MoneyUnit) where
  goods : ℝ
  services : ℝ
  hGoodsPos : 0 < goods
  hServicesPos : 0 < services

/-- Physical quantities of goods and services -/
structure Basket where
  goods : ℝ
  services : ℝ
  hGoodsPos : 0 < goods
  hServicesPos : 0 < services

def basketCost {u : MoneyUnit} (p : Prices u) (b : Basket) : Money u :=
  ⟨p.goods * b.goods + p.services * b.services⟩

@[simp]
theorem basketCost_val {u : MoneyUnit} (p : Prices u) (b : Basket) :
  (basketCost p b).val = p.goods * b.goods + p.services * b.services := rfl

/-- Rupees per PPP dollar weighted by basket `b` -/
def pppRate (ip : Prices .rupee) (up : Prices .ppp) (b : Basket) : Rate .rupee .ppp :=
  ⟨(basketCost ip b).val / (basketCost up b).val⟩

@[simp]
theorem pppRate_val (ip : Prices .rupee) (up : Prices .ppp) (b : Basket) :
    (pppRate ip up b).val = (basketCost ip b).val / (basketCost up b).val :=
  rfl

/-- Poverty line in PPP dollars as the poor basket at US prices -/
def pppLine (up : Prices .ppp) (pb : Basket) : Money .ppp :=
  basketCost up pb

/-- Poverty line of basket `pb` in rupees using the PPP weighted by basket `ab` -/
def localLine (ip : Prices .rupee) (up : Prices .ppp)
    (pb ab : Basket) : Money .rupee :=
  convert (pppRate ip up ab) (pppLine up pb)

def goodsPriceRatio (ip : Prices .rupee) (up : Prices .ppp) : ℝ :=
  ip.goods / up.goods

def servicesPriceRatio (ip : Prices .rupee) (up : Prices .ppp) : ℝ :=
  ip.services / up.services

def goodsShare {u : MoneyUnit} (p : Prices u) (b : Basket) : ℝ :=
  p.goods * b.goods / (basketCost p b).val

def servicesShare {u : MoneyUnit} (p : Prices u) (b : Basket) : ℝ :=
  p.services * b.services / (basketCost p b).val

theorem basketCost_pos {u : MoneyUnit} (p : Prices u) (b : Basket) :
    0 < (basketCost p b).val := by
  have := p.hGoodsPos
  have := b.hGoodsPos
  have := p.hServicesPos
  have := b.hServicesPos
  simp only [basketCost]
  positivity

theorem basketCost_ne_zero {u : MoneyUnit} (p : Prices u) (b : Basket) :
    (basketCost p b).val ≠ 0 := by
  exact ne_of_gt (basketCost_pos p b)

theorem goodsShare_add_servicesShare {u : MoneyUnit} (p : Prices u) (b : Basket) :
    goodsShare p b + servicesShare p b = 1 := by
  have := basketCost_ne_zero p b
  simp only [goodsShare, servicesShare]
  field_simp
  simp only [basketCost]

/-- PPP is the share weighted average of the two price ratios -/
theorem pppRate_eq_sum_shares
  (ip : Prices .rupee)
  (up : Prices .ppp)
  (b : Basket) :
  (pppRate ip up b).val
    = goodsPriceRatio ip up * goodsShare up b
    + servicesPriceRatio ip up * servicesShare up b := by
  have := up.hGoodsPos
  have := up.hServicesPos
  simp only [pppRate, goodsPriceRatio, servicesPriceRatio, goodsShare, servicesShare]
  field_simp
  simp only [basketCost]

/-- PPP rises with the goods share at slope goods ratio minus services ratio -/
theorem pppRate_eq_affine (ip : Prices .rupee) (up : Prices .ppp) (b : Basket) :
    (pppRate ip up b).val
    = servicesPriceRatio ip up
    + goodsShare up b * (goodsPriceRatio ip up - servicesPriceRatio ip up) := by
  rw [pppRate_eq_sum_shares]
  have hShare : goodsShare up b = 1 - servicesShare up b := by
    exact eq_sub_of_add_eq (goodsShare_add_servicesShare up b)
  rw [hShare]
  ring

/-- With the poor basket as PPP weights the line is the poor basket cost in India -/
theorem localLine_self (ip : Prices .rupee) (up : Prices .ppp)
    (b : Basket) :
    localLine ip up b b = basketCost ip b := by
  ext
  simp only [localLine, convert, pppRate, pppLine, basketCost]
  apply div_mul_cancel₀
  exact basketCost_ne_zero up b

/-- The average basket PPP gives a lower line than the poor basket PPP -/
theorem official_lt_poor
    (ip : Prices .rupee)
    (up : Prices .ppp)
    (pb ab : Basket)
    (hPrice : servicesPriceRatio ip up < goodsPriceRatio ip up)
    (hShare : goodsShare up ab < goodsShare up pb) :
    localLine ip up pb ab < localLine ip up pb pb := by
  simp only [localLine, convert, Money.lt_def]
  gcongr
  · simp only [pppLine]
    apply basketCost_pos
  · rw [pppRate_eq_affine, pppRate_eq_affine]
    gcongr

/-- PPP gap is the share gap times the price ratio gap -/
theorem pppRate_gap
    (ip : Prices .rupee)
    (up : Prices .ppp)
    (pb ab : Basket) :
    (pppRate ip up pb).val - (pppRate ip up ab).val
      = (goodsShare up pb - goodsShare up ab)
        * (goodsPriceRatio ip up - servicesPriceRatio ip up) := by
  simp only [pppRate_eq_affine]
  ring

/-- Line gap in rupees is the PPP gap times the PPP line -/
theorem localLine_gap
  (ip : Prices .rupee)
  (up : Prices .ppp)
  (pb ab : Basket) :
  (localLine ip up pb pb).val - (localLine ip up pb ab).val
    = (goodsShare up pb - goodsShare up ab)
      * (goodsPriceRatio ip up - servicesPriceRatio ip up)
      * (pppLine up pb).val := by
  simp only [localLine, convert, pppRate_eq_affine]
  ring

def exIndia : Prices .rupee := ⟨30, 13, by norm_num, by norm_num⟩

def exUS : Prices .ppp := ⟨1, 1, by norm_num, by norm_num⟩

def exPoor : Basket := ⟨78, 22, by norm_num, by norm_num⟩

def exAvg : Basket := ⟨67, 33, by norm_num, by norm_num⟩

example : (pppRate exIndia exUS exPoor).val = 2626 / 100 := by
  norm_num [pppRate_val, basketCost_val, exIndia, exUS, exPoor]

example : (pppRate exIndia exUS exAvg).val = 2439 / 100 := by
  norm_num [pppRate_val, basketCost_val, exIndia, exUS, exAvg]

example : localLine exIndia exUS exPoor exAvg < localLine exIndia exUS exPoor exPoor :=
  official_lt_poor exIndia exUS exPoor exAvg
    (by norm_num [servicesPriceRatio, goodsPriceRatio, exIndia, exUS])
    (by norm_num [goodsShare, basketCost_val, exUS, exPoor, exAvg])

example : (localLine exIndia exUS exPoor exPoor).val
    - (localLine exIndia exUS exPoor exAvg).val = 187 := by
  norm_num [localLine, convert_val, pppLine, pppRate_val, basketCost_val,
    exIndia, exUS, exPoor, exAvg]

end PovertyPPP
