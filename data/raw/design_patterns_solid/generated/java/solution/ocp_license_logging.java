// DesignPatternsSolid | kind=solid | label=ocp | domain=license | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface LicenseDiscount {
    int apply(int price);
}

class LicenseNoDiscount implements LicenseDiscount {
    public int apply(int price) { return price; }
}

class LicenseTenPercent implements LicenseDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class LicensePriceEngine {
    private final LicenseDiscount discount;
    public LicensePriceEngine(LicenseDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "license"; }
}
