// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=profile | tier=minimal
package org.example.patterns;

public final class ProfileSingleton {
    private static ProfileSingleton instance;
    private String value = "default";

    private ProfileSingleton() {}

    public static synchronized ProfileSingleton getInstance() {
        if (instance == null) {
            instance = new ProfileSingleton();
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
