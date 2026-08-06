// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=video | tier=errors
package org.example.patterns;

interface VideoStrategy {
    int apply(int amount);
}

class VideoNormalStrategy implements VideoStrategy {
    public int apply(int amount) { return amount; }
}

class VideoDiscountStrategy implements VideoStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class VideoContext {
    private VideoStrategy strategy;
    public VideoContext(VideoStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(VideoStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "video-strategy"; }
}
