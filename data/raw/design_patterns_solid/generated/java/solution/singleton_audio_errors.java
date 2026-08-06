// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=audio | tier=errors
package org.example.patterns;

public final class AudioSingleton {
    private static AudioSingleton instance;
    private String value = "default";

    private AudioSingleton() {}

    public static synchronized AudioSingleton getInstance() {
        if (instance == null) {
            instance = new AudioSingleton();
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
