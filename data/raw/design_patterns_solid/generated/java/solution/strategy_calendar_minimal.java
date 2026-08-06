// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=calendar | tier=minimal
package org.example.patterns;

interface CalendarStrategy {
    int apply(int amount);
}

class CalendarNormalStrategy implements CalendarStrategy {
    public int apply(int amount) { return amount; }
}

class CalendarDiscountStrategy implements CalendarStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class CalendarContext {
    private CalendarStrategy strategy;
    public CalendarContext(CalendarStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(CalendarStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "calendar-strategy"; }
}
