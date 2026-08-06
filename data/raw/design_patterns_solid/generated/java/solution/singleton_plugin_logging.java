// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=plugin | tier=logging
package org.example.patterns;

public final class PluginSingleton {
    private static PluginSingleton instance;
    private String value = "default";

    private PluginSingleton() {}

    public static synchronized PluginSingleton getInstance() {
        if (instance == null) {
            instance = new PluginSingleton();
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
