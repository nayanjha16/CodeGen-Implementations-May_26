// DesignPatternsSolid | kind=design_pattern | label=strategy | domain=notifications | tier=minimal
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
        return strategy.apply(amount);
    }
    public String tag() { return "notifications-strategy"; }
}
