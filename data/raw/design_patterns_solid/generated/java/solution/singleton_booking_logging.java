// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=booking | tier=logging
package org.example.patterns;

public final class BookingSingleton {
    private static BookingSingleton instance;
    private String value = "default";

    private BookingSingleton() {}

    public static synchronized BookingSingleton getInstance() {
        if (instance == null) {
            instance = new BookingSingleton();
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
