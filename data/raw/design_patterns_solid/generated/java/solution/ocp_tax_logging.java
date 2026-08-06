// DesignPatternsSolid | kind=solid | label=ocp | domain=tax | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface TaxDiscount {
    int apply(int price);
}

class TaxNoDiscount implements TaxDiscount {
    public int apply(int price) { return price; }
}

class TaxTenPercent implements TaxDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class TaxPriceEngine {
    private final TaxDiscount discount;
    public TaxPriceEngine(TaxDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "tax"; }
}
