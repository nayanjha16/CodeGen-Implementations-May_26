// DesignPatternsSolid | kind=solid | label=ocp | domain=discount | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface DiscountDiscount {
    int apply(int price);
}

class DiscountNoDiscount implements DiscountDiscount {
    public int apply(int price) { return price; }
}

class DiscountTenPercent implements DiscountDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class DiscountPriceEngine {
    private final DiscountDiscount discount;
    public DiscountPriceEngine(DiscountDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "discount"; }
}
