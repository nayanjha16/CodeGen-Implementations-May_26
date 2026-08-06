// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=config | tier=minimal
package org.example.patterns;

interface ConfigStrategy {
    int apply(int amount);
}

class ConfigNormalStrategy implements ConfigStrategy {
    public int apply(int amount) { return amount; }
}

class ConfigDiscountStrategy implements ConfigStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class ConfigContext {
    private ConfigStrategy strategy;
    public ConfigContext(ConfigStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(ConfigStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "config-strategy"; }
}
