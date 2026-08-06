// DesignPatternsSolid | kind=solid | label=ocp | domain=auth | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface AuthDiscount {
    int apply(int price);
}

class AuthNoDiscount implements AuthDiscount {
    public int apply(int price) { return price; }
}

class AuthTenPercent implements AuthDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class AuthPriceEngine {
    private final AuthDiscount discount;
    public AuthPriceEngine(AuthDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "auth"; }
}
