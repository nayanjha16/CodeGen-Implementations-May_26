// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=sensors | tier=logging
package org.example.patterns;

interface SensorsStrategy {
    int apply(int amount);
}

class SensorsNormalStrategy implements SensorsStrategy {
    public int apply(int amount) { return amount; }
}

class SensorsDiscountStrategy implements SensorsStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class SensorsContext {
    private SensorsStrategy strategy;
    public SensorsContext(SensorsStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(SensorsStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "sensors-strategy"; }
}
