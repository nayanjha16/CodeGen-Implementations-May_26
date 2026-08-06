// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=tax | tier=minimal
package org.example.patterns;

public final class TaxSingleton {
    private static TaxSingleton instance;
    private String value = "default";

    private TaxSingleton() {}

    public static synchronized TaxSingleton getInstance() {
        if (instance == null) {
            instance = new TaxSingleton();
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
