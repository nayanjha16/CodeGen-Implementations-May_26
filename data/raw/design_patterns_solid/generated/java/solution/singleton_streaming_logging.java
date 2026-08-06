// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=streaming | tier=logging
package org.example.patterns;

public final class StreamingSingleton {
    private static StreamingSingleton instance;
    private String value = "default";

    private StreamingSingleton() {}

    public static synchronized StreamingSingleton getInstance() {
        if (instance == null) {
            instance = new StreamingSingleton();
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
