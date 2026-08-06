// DesignPatternsSolid | kind=solid | label=ocp | domain=analytics | tier=minimal
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface AnalyticsDiscount {
    int apply(int price);
}

class AnalyticsNoDiscount implements AnalyticsDiscount {
    public int apply(int price) { return price; }
}

class AnalyticsTenPercent implements AnalyticsDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class AnalyticsPriceEngine {
    private final AnalyticsDiscount discount;
    public AnalyticsPriceEngine(AnalyticsDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "analytics"; }
}
