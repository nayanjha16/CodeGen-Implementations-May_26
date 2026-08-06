// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=editor | tier=errors
package org.example.patterns;

public final class EditorSingleton {
    private static EditorSingleton instance;
    private String value = "default";

    private EditorSingleton() {}

    public static synchronized EditorSingleton getInstance() {
        if (instance == null) {
            instance = new EditorSingleton();
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
