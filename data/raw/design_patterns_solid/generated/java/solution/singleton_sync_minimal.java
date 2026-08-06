// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=sync | tier=minimal
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
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
