// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=booking | tier=minimal
package org.example.patterns;

interface BookingStrategy {
    int apply(int amount);
}

class BookingNormalStrategy implements BookingStrategy {
    public int apply(int amount) { return amount; }
}

class BookingDiscountStrategy implements BookingStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class BookingContext {
    private BookingStrategy strategy;
    public BookingContext(BookingStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(BookingStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        return strategy.apply(amount);
    }
    public String tag() { return "booking-strategy"; }
}
