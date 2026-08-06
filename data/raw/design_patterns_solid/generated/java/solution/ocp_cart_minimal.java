// DesignPatternsSolid | kind=solid | label=ocp | domain=cart | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface CartDiscount {
    int apply(int price);
}

class CartNoDiscount implements CartDiscount {
    public int apply(int price) { return price; }
}

class CartTenPercent implements CartDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class CartPriceEngine {
    private final CartDiscount discount;
    public CartPriceEngine(CartDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "cart"; }
}
