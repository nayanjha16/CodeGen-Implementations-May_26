// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=chat | tier=minimal
package org.example.patterns;

public final class ChatSingleton {
    private static ChatSingleton instance;
    private String value = "default";

    private ChatSingleton() {}

    public static synchronized ChatSingleton getInstance() {
        if (instance == null) {
            instance = new ChatSingleton();
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
