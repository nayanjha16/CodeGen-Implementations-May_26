// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=email | tier=logging
package org.example.patterns;

public final class EmailSingleton {
    private static EmailSingleton instance;
    private String value = "default";

    private EmailSingleton() {}

    public static synchronized EmailSingleton getInstance() {
        if (instance == null) {
            instance = new EmailSingleton();
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
