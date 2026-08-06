// DesignPatternsSolid | kind=solid | label=ocp | domain=shipping | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface ShippingDiscount {
    int apply(int price);
}

class ShippingNoDiscount implements ShippingDiscount {
    public int apply(int price) { return price; }
}

class ShippingTenPercent implements ShippingDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class ShippingPriceEngine {
    private final ShippingDiscount discount;
    public ShippingPriceEngine(ShippingDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "shipping"; }
}
