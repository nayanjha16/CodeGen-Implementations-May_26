// DesignPatternsSolid | kind=solid | label=ocp | domain=cache | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface CacheDiscount {
    int apply(int price);
}

class CacheNoDiscount implements CacheDiscount {
    public int apply(int price) { return price; }
}

class CacheTenPercent implements CacheDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class CachePriceEngine {
    private final CacheDiscount discount;
    public CachePriceEngine(CacheDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "cache"; }
}
