// DesignPatternsSolid | kind=solid | label=ocp | domain=wallet | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface WalletDiscount {
    int apply(int price);
}

class WalletNoDiscount implements WalletDiscount {
    public int apply(int price) { return price; }
}

class WalletTenPercent implements WalletDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class WalletPriceEngine {
    private final WalletDiscount discount;
    public WalletPriceEngine(WalletDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "wallet"; }
}
