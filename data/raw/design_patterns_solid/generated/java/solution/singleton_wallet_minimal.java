// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=wallet | tier=minimal
package org.example.patterns;

public final class WalletSingleton {
    private static WalletSingleton instance;
    private String value = "default";

    private WalletSingleton() {}

    public static synchronized WalletSingleton getInstance() {
        if (instance == null) {
            instance = new WalletSingleton();
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
