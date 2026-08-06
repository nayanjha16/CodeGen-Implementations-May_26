// DesignPatternsSolid | kind=solid | label=ocp | domain=metrics | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface MetricsDiscount {
    int apply(int price);
}

class MetricsNoDiscount implements MetricsDiscount {
    public int apply(int price) { return price; }
}

class MetricsTenPercent implements MetricsDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class MetricsPriceEngine {
    private final MetricsDiscount discount;
    public MetricsPriceEngine(MetricsDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "metrics"; }
}
