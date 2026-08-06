// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=logging | tier=logging
package org.example.patterns;

public final class LoggingSingleton {
    private static LoggingSingleton instance;
    private String value = "default";

    private LoggingSingleton() {}

    public static synchronized LoggingSingleton getInstance() {
        if (instance == null) {
            instance = new LoggingSingleton();
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
