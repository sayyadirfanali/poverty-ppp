# poverty-ppp

**Lean 4** formalisation of the **plutocratic bias** argument in India's poverty line debate.

It proves the exact conditions under which the PPP conversion rate using an average consumption basket underestimates the cost of living for poor households, and calibrates the resulting gap using Indian survey data.

## The Problem

Plutocratic bias is a longstanding criticism of the World Bank's international poverty line, which is expressed in PPP dollars. The consumption basket used to construct PPP can underestimate the true conversion rate for poorer households, and hence underestimate both the poverty line and the poverty headcount.

Arun Kumar recently restated this problem for India: low wages in India make personal services cheap, while everyday goods remain relatively expensive compared with US prices. Because poor households spend almost exclusively on basic goods rather than services, applying an average PPP rate makes their cost of living look artificially low.

Formalising this argument in Lean 4 separates the **logical deduction** (checked mechanically from the definitions) from the **empirical assumptions** (documented under Scope and Limitations).

## Model

Household spending is divided into **goods** ($g$) and **services** ($s$), with rupee-to-dollar price ratios $r_g$ and $r_s$.
For a household whose consumption basket has a US-price goods share $w \in (0, 1)$, its effective PPP rate is:

$$\text{PPP}(w) = w \cdot r_g + (1 - w) \cdot r_s$$

Comparing the poorest households ($w_{\text{poor}}$) against the average household ($w_{\text{avg}}$) yields the **PPP gap**:

$$\text{PPP}_{\text{poor}} - \text{PPP}_{\text{avg}} = (w_{\text{poor}} - w_{\text{avg}}) \times (r_g - r_s)$$

Whenever $w_{\text{poor}} > w_{\text{avg}}$ and $r_g > r_s$, the poor face a strictly higher PPP rate—and a higher rupee poverty line—than the official conversion implies.

## Empirical Verification

Using goods and services price ratios built from 2021 International Comparison Program (ICP) heading-level PPPs ($r_g = 30.1$, $r_s = 13.2$) and Indian-rupee spending shares ($s_g$) from the 2022–23 Household Consumption Expenditure Survey (HCES), `calibrate.py` converts Indian-price shares into US-price shares via $w = \frac{s_g / r_g}{s_g / r_g + (1 - s_g) / r_s}$ and computes the sector-level gaps:

![PPP of a basket against its goods share](ppp_chart.svg)

| Measure | Rural India | Urban India |
|---|---:|---:|
| Goods share, poorest 10% (at Indian prices, $s_g$) | 89% | 85% |
| Goods share, average household (at Indian prices, $s_g$) | 82% | 72% |
| Goods share, poorest 10% (at US prices, $w_{\text{poor}}$) | 77.6% | 70.8% |
| Goods share, average household (at US prices, $w_{\text{avg}}$) | 66.7% | 53.5% |
| PPP rate, average household | ₹24.48 / $ | ₹22.29 / $ |
| PPP rate, poorest 10% | ₹26.32 / $ | ₹25.20 / $ |
| **PPP gap** | **+7.5%** | **+13.1%** |

`PovertyPPP.lean` also verifies a worked numerical case on every build.

The fact that rural PPP comes out higher than urban is an artefact of applying single national price ratios from ICP 2021 to both sectors.

## Theorems (`PovertyPPP.lean`)

| Theorem | What It Proves |
|---|---|
| `pppRate_eq_sum_shares` | A basket's PPP rate equals $w_g \cdot r_g + w_s \cdot r_s$. |
| `pppRate_eq_affine` | Since $w_g + w_s = 1$, the PPP rate equals $r_s + w_g \cdot (r_g - r_s)$. |
| `localLine_self` | Using the poor basket as PPP weights sets the rupee poverty line equal to the poor basket's rupee cost. |
| `official_lt_poor` | If $w_{\text{poor}} > w_{\text{avg}}$ and $r_g > r_s$, the poor's PPP rate and resulting rupee poverty line are strictly higher than the official rate. |
| `pppRate_gap` | $\text{PPP}_{\text{poor}} - \text{PPP}_{\text{avg}} = (w_{\text{poor}} - w_{\text{avg}}) \times (r_g - r_s)$. |
| `localLine_gap` | The rupee poverty line gap equals the PPP gap multiplied by the international poverty line in PPP dollars. |

## Scope and Limitations

- Fixed two-category basket with uniform national price ratios rather than multilateral **GEKS-Fisher** index.
- 2021 ICP prices paired with 2022–23 HCES shares and mixed categories split by assumption, and housing omitted (imputed rent in HCES).
- World Bank global poverty line is aggregated from poor countries and can dampen the net effect on India's line (Deaton and Dupriez, 2011).

## Usage

```bash
# Verify Lean 4 proofs
lake exe cache get && lake build

# Regenerate calibration table and chart
pip install -r requirements.txt && python3 calibrate.py && python3 chart.py
```

## Sources

- **Arun Kumar**, [In India, Poor Are Less Poor Because They Earn Little](https://thewire.in/economy/in-india-poor-are-less-poor-because-they-earn-little), *The Wire*, 4 November 2026.
- **World Bank**, [International Comparison Program 2021, detailed results](https://databank.worldbank.org/embed/ICP-2021-Cycle/id/3a11040d?inf=n).
- **MoSPI**, [Household Consumption Expenditure Survey 2022-23, NSS Report 591](https://www.mospi.gov.in/sites/default/files/publication_reports/Report_591_HCES_2022-23New.pdf), Table A6.
- **Angus Deaton and Olivier Dupriez**, "Purchasing Power Parity Exchange Rates for the Global Poor", *American Economic Journal: Applied Economics* 3(2), 2011, pp. 137–166.

## Authorship

I formulated the economic model and wrote the core Lean 4 definitions and proofs. Claude and Gemini assisted with proof structuring, Python scripting, and README drafting. I have manually verified all definitions, proofs, and scripts against the claims stated here.

## Contact

Irfan Ali | [irfanali.org](https://irfanali.org)

Corrections are welcome, especially regarding the formalisation. Please open an issue on GitHub or email me.
