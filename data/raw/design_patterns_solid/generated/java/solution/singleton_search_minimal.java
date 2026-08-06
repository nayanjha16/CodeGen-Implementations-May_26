// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=search | tier=minimal
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
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
