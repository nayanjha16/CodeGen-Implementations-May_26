// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=http | tier=minimal
package org.example.patterns;

public final class HttpSingleton {
    private static HttpSingleton instance;
    private String value = "default";

    private HttpSingleton() {}

    public static synchronized HttpSingleton getInstance() {
        if (instance == null) {
            instance = new HttpSingleton();
        }
        return instance;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
