// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=logging | tier=minimal
package org.example.patterns;

interface LoggingStrategy {
    int apply(int amount);
}

class LoggingNormalStrategy implements LoggingStrategy {
    public int apply(int amount) { return amount; }
}

class LoggingDiscountStrategy implements LoggingStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class LoggingContext {
    private LoggingStrategy strategy;
    public LoggingContext(LoggingStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(LoggingStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "logging-strategy"; }
}
