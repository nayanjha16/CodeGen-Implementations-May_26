// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=shipping | tier=errors
package org.example.patterns;

public final class ShippingSingleton {
    private static ShippingSingleton instance;
    private String value = "default";

    private ShippingSingleton() {}

    public static synchronized ShippingSingleton getInstance() {
        if (instance == null) {
            instance = new ShippingSingleton();
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
