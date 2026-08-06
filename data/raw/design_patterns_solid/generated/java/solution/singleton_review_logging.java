// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=review | tier=logging
package org.example.patterns;

public final class ReviewSingleton {
    private static ReviewSingleton instance;
    private String value = "default";

    private ReviewSingleton() {}

    public static synchronized ReviewSingleton getInstance() {
        if (instance == null) {
            instance = new ReviewSingleton();
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
