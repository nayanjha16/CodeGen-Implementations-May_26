// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=cache | tier=errors
package org.example.patterns;

interface CacheStrategy {
    int apply(int amount);
}

class CacheNormalStrategy implements CacheStrategy {
    public int apply(int amount) { return amount; }
}

class CacheDiscountStrategy implements CacheStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class CacheContext {
    private CacheStrategy strategy;
    public CacheContext(CacheStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(CacheStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "cache-strategy"; }
}
