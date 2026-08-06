// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=storage | tier=errors
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
        if (value == null || value.isEmpty()) throw new IllegalArgumentException("value required");
        this.value = value;
        System.out.println("[log] set " + value);
    }

    public String getValue() {
        return value;
    }
}
