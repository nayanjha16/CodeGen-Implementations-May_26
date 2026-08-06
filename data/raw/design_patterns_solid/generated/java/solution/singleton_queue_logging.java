// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=queue | tier=logging
package org.example.patterns;

public final class QueueSingleton {
    private static QueueSingleton instance;
    private String value = "default";

    private QueueSingleton() {}

    public static synchronized QueueSingleton getInstance() {
        if (instance == null) {
            instance = new QueueSingleton();
        }
        return instance;
    }

    public void setValue(String value) {
        this.value = value;
        System.out.println("[log] set " + value);
    }

    public String getValue() {
        return value;
    }
}
