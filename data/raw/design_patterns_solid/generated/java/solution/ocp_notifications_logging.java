// DesignPatternsSolid | kind=solid | label=ocp | domain=notifications | tier=logging
package org.example.patterns;

// OCP: extend via new discount policy without editing engine
interface NotificationsDiscount {
    int apply(int price);
}

class NotificationsNoDiscount implements NotificationsDiscount {
    public int apply(int price) { return price; }
}

class NotificationsTenPercent implements NotificationsDiscount {
    public int apply(int price) { return price - price / 10; }
}

public class NotificationsPriceEngine {
    private final NotificationsDiscount discount;
    public NotificationsPriceEngine(NotificationsDiscount discount) { this.discount = discount; }
    public int quote(int price) { return discount.apply(price); }
    public String domain() { return "notifications"; }
}
