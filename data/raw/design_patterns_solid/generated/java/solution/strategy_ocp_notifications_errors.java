// DesignPatternsSolid | kind=combo | label=strategy+ocp | domain=notifications | tier=errors
package org.example.patterns;

interface NotificationsStrategy {
    int apply(int amount);
}

class NotificationsNormalStrategy implements NotificationsStrategy {
    public int apply(int amount) { return amount; }
}

class NotificationsDiscountStrategy implements NotificationsStrategy {
    public int apply(int amount) { return amount / 2; }
}

public class NotificationsContext {
    private NotificationsStrategy strategy;
    public NotificationsContext(NotificationsStrategy strategy) { this.strategy = strategy; }
    public void setStrategy(NotificationsStrategy strategy) { this.strategy = strategy; }
    public int execute(int amount) {
        if (amount < 0) throw new IllegalArgumentException("amount >= 0");
        return strategy.apply(amount);
    }
    public String tag() { return "notifications-strategy"; }
}
