// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=widgets | tier=minimal
package org.example.patterns;

public final class WidgetsSingleton {
    private static WidgetsSingleton instance;
    private String value = "default";

    private WidgetsSingleton() {}

    public static synchronized WidgetsSingleton getInstance() {
        if (instance == null) {
            instance = new WidgetsSingleton();
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
