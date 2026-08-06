// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=discount | tier=logging
package org.example.patterns;

public final class DiscountSingleton {
    private static DiscountSingleton instance;
    private String value = "default";

    private DiscountSingleton() {}

    public static synchronized DiscountSingleton getInstance() {
        if (instance == null) {
            instance = new DiscountSingleton();
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
