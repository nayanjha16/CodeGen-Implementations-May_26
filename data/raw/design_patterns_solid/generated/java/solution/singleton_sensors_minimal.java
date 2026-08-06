// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=sensors | tier=minimal
package org.example.patterns;

public final class SensorsSingleton {
    private static SensorsSingleton instance;
    private String value = "default";

    private SensorsSingleton() {}

    public static synchronized SensorsSingleton getInstance() {
        if (instance == null) {
            instance = new SensorsSingleton();
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
