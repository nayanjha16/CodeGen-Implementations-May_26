// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=storage | tier=minimal
package org.example.patterns;

public final class StorageSingleton {
    private static StorageSingleton instance;
    private String value = "default";

    private StorageSingleton() {}

    public static synchronized StorageSingleton getInstance() {
        if (instance == null) {
            instance = new StorageSingleton();
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
