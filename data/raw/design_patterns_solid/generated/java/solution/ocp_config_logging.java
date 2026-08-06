// DesignPatternsSolid | kind=solid | label=ocp | domain=config | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface ConfigDiscount {
    int apply(int price);
}

class ConfigNoDiscount implements ConfigDiscount {
    public int apply(int price) { return price; }
}

class ConfigTenPercent implements ConfigDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class ConfigPriceEngine {
    private final ConfigDiscount discount;
    public ConfigPriceEngine(ConfigDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "config"; }
}
