// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=cart | tier=logging
package org.example.patterns;

public final class CartSingleton {
    private static CartSingleton instance;
    private String value = "default";

    private CartSingleton() {}

    public static synchronized CartSingleton getInstance() {
        if (instance == null) {
            instance = new CartSingleton();
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
