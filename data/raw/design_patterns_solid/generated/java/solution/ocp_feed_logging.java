// DesignPatternsSolid | kind=solid | label=ocp | domain=feed | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface FeedDiscount {
    int apply(int price);
}

class FeedNoDiscount implements FeedDiscount {
    public int apply(int price) { return price; }
}

class FeedTenPercent implements FeedDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class FeedPriceEngine {
    private final FeedDiscount discount;
    public FeedPriceEngine(FeedDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "feed"; }
}
