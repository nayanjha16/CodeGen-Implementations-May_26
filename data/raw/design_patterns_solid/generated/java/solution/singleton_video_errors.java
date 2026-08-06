// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=video | tier=errors
package org.example.patterns;

public final class VideoSingleton {
    private static VideoSingleton instance;
    private String value = "default";

    private VideoSingleton() {}

    public static synchronized VideoSingleton getInstance() {
        if (instance == null) {
            instance = new VideoSingleton();
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
