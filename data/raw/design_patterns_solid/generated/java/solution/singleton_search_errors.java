// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=search | tier=errors
package org.example.patterns;

public final class SearchSingleton {
    private static SearchSingleton instance;
    private String value = "default";

    private SearchSingleton() {}

    public static synchronized SearchSingleton getInstance() {
        if (instance == null) {
            instance = new SearchSingleton();
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
