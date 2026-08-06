// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=config | tier=errors
package org.example.patterns;

public final class ConfigSingleton {
    private static ConfigSingleton instance;
    private String value = "default";

    private ConfigSingleton() {}

    public static synchronized ConfigSingleton getInstance() {
        if (instance == null) {
            instance = new ConfigSingleton();
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
