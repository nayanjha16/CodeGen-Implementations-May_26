// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=streaming | tier=errors
package org.example.patterns;

interface StreamingStrategy {
    int apply(int amount);
}

class StreamingNormalStrategy implements StreamingStrategy {
    public int apply(int amount) { return amount; }
}

class StreamingDiscountStrategy implements StreamingStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class StreamingContext {
    private StreamingStrategy strategy;
    public StreamingContext(StreamingStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(StreamingStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "streaming-strategy"; }
}
