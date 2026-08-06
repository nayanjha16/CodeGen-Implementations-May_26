// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=http | tier=errors
package org.example.patterns;

interface HttpStrategy {
    int apply(int amount);
}

class HttpNormalStrategy implements HttpStrategy {
    public int apply(int amount) { return amount; }
}

class HttpDiscountStrategy implements HttpStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class HttpContext {
    private HttpStrategy strategy;
    public HttpContext(HttpStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(HttpStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "http-strategy"; }
}
