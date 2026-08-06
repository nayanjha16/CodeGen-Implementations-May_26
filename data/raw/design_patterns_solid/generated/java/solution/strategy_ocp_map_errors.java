// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=map | tier=errors
package org.example.patterns;

interface MapStrategy {
    int apply(int amount);
}

class MapNormalStrategy implements MapStrategy {
    public int apply(int amount) { return amount; }
}

class MapDiscountStrategy implements MapStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class MapContext {
    private MapStrategy strategy;
    public MapContext(MapStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(MapStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "map-strategy"; }
}
