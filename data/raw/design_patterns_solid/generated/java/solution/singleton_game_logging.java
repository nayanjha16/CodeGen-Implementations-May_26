// DesignPatternsSolid | kind=design_pattern | label=singleton | domain=game | tier=logging
package org.example.patterns;

public final class GameSingleton {
    private static GameSingleton instance;
    private String value = "default";

    private GameSingleton() {}

    public static synchronized GameSingleton getInstance() {
        if (instance == null) {
            instance = new GameSingleton();
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
