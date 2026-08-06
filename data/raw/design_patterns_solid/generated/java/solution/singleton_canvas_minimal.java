// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=canvas | tier=minimal
package org.example.patterns;

public final class CanvasSingleton {
    private static CanvasSingleton instance;
    private String value = "default";

    private CanvasSingleton() {}

    public static synchronized CanvasSingleton getInstance() {
        if (instance == null) {
            instance = new CanvasSingleton();
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
