// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=plugin | tier=errors
package org.example.patterns;

interface PluginStrategy {
    int apply(int amount);
}

class PluginNormalStrategy implements PluginStrategy {
    public int apply(int amount) { return amount; }
}

class PluginDiscountStrategy implements PluginStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class PluginContext {
    private PluginStrategy strategy;
    public PluginContext(PluginStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(PluginStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "plugin-strategy"; }
}
