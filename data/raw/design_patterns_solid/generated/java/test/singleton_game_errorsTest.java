package org.example.patterns;
public class GameSingletonTest {
    public static void main(String[] args) {
        GameSingleton a = GameSingleton.getInstance();
        GameSingleton b = GameSingleton.getInstance();
        a.setValue("game-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("game-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
