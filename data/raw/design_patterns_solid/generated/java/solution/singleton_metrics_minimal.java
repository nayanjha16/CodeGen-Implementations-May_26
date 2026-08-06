// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=metrics | tier=minimal
package org.example.patterns;

public final class MetricsSingleton {
    private static MetricsSingleton instance;
    private String value = "default";

    private MetricsSingleton() {}

    public static synchronized MetricsSingleton getInstance() {
        if (instance == null) {
            instance = new MetricsSingleton();
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
