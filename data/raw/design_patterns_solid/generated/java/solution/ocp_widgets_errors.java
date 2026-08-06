// DesignPatternsSolid | kind=solid | label=ocp | domain=widgets | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface WidgetsDiscount {
    int apply(int price);
}

class WidgetsNoDiscount implements WidgetsDiscount {
    public int apply(int price) { return price; }
}

class WidgetsTenPercent implements WidgetsDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class WidgetsPriceEngine {
    private final WidgetsDiscount discount;
    public WidgetsPriceEngine(WidgetsDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "widgets"; }
}
