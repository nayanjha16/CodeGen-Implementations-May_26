// DesignPatternsSolid | kind=solid | label=ocp | domain=plugin | tier=errors
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface PluginDiscount {
    int apply(int price);
}

class PluginNoDiscount implements PluginDiscount {
    public int apply(int price) { return price; }
}

class PluginTenPercent implements PluginDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class PluginPriceEngine {
    private final PluginDiscount discount;
    public PluginPriceEngine(PluginDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "plugin"; }
}
