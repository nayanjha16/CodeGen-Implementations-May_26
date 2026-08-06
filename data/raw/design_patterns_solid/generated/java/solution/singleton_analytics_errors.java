// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=analytics | tier=errors
package org.example.patterns;

public final class AnalyticsSingleton {
    private static AnalyticsSingleton instance;
    private String value = "default";

    private AnalyticsSingleton() {}

    public static synchronized AnalyticsSingleton getInstance() {
        if (instance == null) {
            instance = new AnalyticsSingleton();
        }
        return instance;
    }

    public void setValue(String value) {
        if (value == null || value.isEmpty()) throw new IllegalArgumentException("value required");
        this.value = value;
        System.out.println("[log] set " + value);
    }

    public String getValue() {
        return value;
    }
}
