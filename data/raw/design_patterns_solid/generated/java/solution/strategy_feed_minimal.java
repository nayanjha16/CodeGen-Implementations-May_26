// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=feed | tier=minimal
package org.example.patterns;

interface FeedStrategy {
    int apply(int amount);
}

class FeedNormalStrategy implements FeedStrategy {
    public int apply(int amount) { return amount; }
}

class FeedDiscountStrategy implements FeedStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class FeedContext {
    private FeedStrategy strategy;
    public FeedContext(FeedStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(FeedStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "feed-strategy"; }
}
