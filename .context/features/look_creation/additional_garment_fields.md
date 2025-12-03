# Additional Fields for Each Garment

## 1. Warmth Level (`calidez`)

A numeric indicator of how warm the garment is.

### Field

-   `warmth`: integer (1--5)

### Values (English)

  Value   Meaning
  ------- ------------------------------------------------
  **1**   very light (summer items, tank tops, sandals)
  **2**   light (linen shirts, thin fabrics)
  **3**   medium (regular long sleeves, denim, sneakers)
  **4**   warm (sweaters, fleece, boots)
  **5**   very warm (coats, down jackets, winter boots)

------------------------------------------------------------------------

## 2. Pattern (`patron`)

Type of pattern applied to the garment.

### Field

-   `pattern`: string (enum)

### Possible Values (English)

-   "solid"
-   "stripes"
-   "checks"
-   "micro_print"
-   "print"

------------------------------------------------------------------------

## (Optional) 3. Pattern Intensity (`patron_intensidad`)

Useful for later harmony rules, but optional.

### Field

-   `pattern_intensity`: integer (1--3)

### Values (English)

  Value   Meaning
  ------- ---------------
  **1**   very subtle
  **2**   medium
  **3**   strong / bold
