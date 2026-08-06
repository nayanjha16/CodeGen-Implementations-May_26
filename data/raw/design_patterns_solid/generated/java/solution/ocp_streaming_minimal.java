// DesignPatternsSolid | kind=solid | label=ocp | domain=streaming | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface StreamingDiscount {
    int apply(int price);
}

class StreamingNoDiscount implements StreamingDiscount {
    public int apply(int price) { return price; }
}

class StreamingTenPercent implements StreamingDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class StreamingPriceEngine {
    private final StreamingDiscount discount;
    public StreamingPriceEngine(StreamingDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "streaming"; }
}
