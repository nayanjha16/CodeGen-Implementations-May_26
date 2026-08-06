// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=database | tier=errors
package org.example.patterns;

public final class DatabaseSingleton {
    private static DatabaseSingleton instance;
    private String value = "default";

    private DatabaseSingleton() {}

    public static synchronized DatabaseSingleton getInstance() {
        if (instance == null) {
            instance = new DatabaseSingleton();
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
