// DesignPatternsSolid | kind=solid | label=ocp | domain=billing | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface BillingDiscount {
    int apply(int price);
}

class BillingNoDiscount implements BillingDiscount {
    public int apply(int price) { return price; }
}

class BillingTenPercent implements BillingDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class BillingPriceEngine {
    private final BillingDiscount discount;
    public BillingPriceEngine(BillingDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "billing"; }
}
