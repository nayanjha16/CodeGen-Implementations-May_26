// DesignPatternsSolid | kind=solid | label=ocp | domain=sync | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface SyncDiscount {
    int apply(int price);
}

class SyncNoDiscount implements SyncDiscount {
    public int apply(int price) { return price; }
}

class SyncTenPercent implements SyncDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class SyncPriceEngine {
    private final SyncDiscount discount;
    public SyncPriceEngine(SyncDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "sync"; }
}
