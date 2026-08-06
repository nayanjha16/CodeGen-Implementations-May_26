// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=todo | tier=logging
package org.example.patterns;

public final class TodoSingleton {
    private static TodoSingleton instance;
    private String value = "default";

    private TodoSingleton() {}

    public static synchronized TodoSingleton getInstance() {
        if (instance == null) {
            instance = new TodoSingleton();
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
