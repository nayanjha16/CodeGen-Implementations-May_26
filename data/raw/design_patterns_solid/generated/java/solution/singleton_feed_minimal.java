// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=feed | tier=minimal
package org.example.patterns;

public final class FeedSingleton {
    private static FeedSingleton instance;
    private String value = "default";

    private FeedSingleton() {}

    public static synchronized FeedSingleton getInstance() {
        if (instance == null) {
            instance = new FeedSingleton();
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
