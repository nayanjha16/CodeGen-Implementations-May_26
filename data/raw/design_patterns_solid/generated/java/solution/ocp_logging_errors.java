// DesignPatternsSolid | kind=solid | label=ocp | domain=logging | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface LoggingDiscount {
    int apply(int price);
}

class LoggingNoDiscount implements LoggingDiscount {
    public int apply(int price) { return price; }
}

class LoggingTenPercent implements LoggingDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class LoggingPriceEngine {
    private final LoggingDiscount discount;
    public LoggingPriceEngine(LoggingDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "logging"; }
}
