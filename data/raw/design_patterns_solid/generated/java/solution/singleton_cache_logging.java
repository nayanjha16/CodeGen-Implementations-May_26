// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=cache | tier=logging
package org.example.patterns;

public final class CacheSingleton {
    private static CacheSingleton instance;
    private String value = "default";

    private CacheSingleton() {}

    public static synchronized CacheSingleton getInstance() {
        if (instance == null) {
            instance = new CacheSingleton();
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
