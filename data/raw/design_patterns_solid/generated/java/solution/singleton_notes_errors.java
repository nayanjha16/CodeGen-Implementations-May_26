// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=notes | tier=errors
package org.example.patterns;

public final class NotesSingleton {
    private static NotesSingleton instance;
    private String value = "default";

    private NotesSingleton() {}

    public static synchronized NotesSingleton getInstance() {
        if (instance == null) {
            instance = new NotesSingleton();
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
