// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=notifications | tier=minimal
package org.example.patterns;

public final class NotificationsSingleton {
    private static NotificationsSingleton instance;
    private String value = "default";

    private NotificationsSingleton() {}

    public static synchronized NotificationsSingleton getInstance() {
        if (instance == null) {
            instance = new NotificationsSingleton();
        }
        return instance;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
