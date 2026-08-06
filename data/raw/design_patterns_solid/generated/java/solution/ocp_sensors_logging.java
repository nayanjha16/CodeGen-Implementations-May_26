// DesignPatternsSolid | kind=solid | label=ocp | domain=sensors | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface SensorsDiscount {
    int apply(int price);
}

class SensorsNoDiscount implements SensorsDiscount {
    public int apply(int price) { return price; }
}

class SensorsTenPercent implements SensorsDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class SensorsPriceEngine {
    private final SensorsDiscount discount;
    public SensorsPriceEngine(SensorsDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "sensors"; }
}
