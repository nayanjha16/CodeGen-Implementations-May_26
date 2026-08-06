// DesignPatternsSolid | kind=design_pattern | label=factory | domain=notifications | tier=errors
package org.example.patterns;

interface NotificationsProduct {
    String operate();
}

class NotificationsBasicProduct implements NotificationsProduct {
    public String operate() { return "basic-notifications"; }
}

class NotificationsPremiumProduct implements NotificationsProduct {
    public String operate() { return "premium-notifications"; }
}

public class NotificationsFactory {
    public NotificationsProduct create(String type) {
        if (type == null || type.isEmpty()) throw new IllegalArgumentException("type required");
        System.out.println("[log] create " + type);
        if ("premium".equalsIgnoreCase(type)) return new NotificationsPremiumProduct();
        return new NotificationsBasicProduct();
    }
}
