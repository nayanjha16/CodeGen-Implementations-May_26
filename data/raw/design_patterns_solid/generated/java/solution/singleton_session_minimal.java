// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=session | tier=minimal
package org.example.patterns;

public final class SessionSingleton {
    private static SessionSingleton instance;
    private String value = "default";

    private SessionSingleton() {}

    public static synchronized SessionSingleton getInstance() {
        if (instance == null) {
            instance = new SessionSingleton();
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
