// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=sync | tier=errors
package org.example.patterns;

public final class SyncSingleton {
    private static SyncSingleton instance;
    private String value = "default";

    private SyncSingleton() {}

    public static synchronized SyncSingleton getInstance() {
        if (instance == null) {
            instance = new SyncSingleton();
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
