// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=map | tier=errors
package org.example.patterns;

public final class MapSingleton {
    private static MapSingleton instance;
    private String value = "default";

    private MapSingleton() {}

    public static synchronized MapSingleton getInstance() {
        if (instance == null) {
            instance = new MapSingleton();
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
