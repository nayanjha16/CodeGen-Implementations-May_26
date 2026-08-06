package org.example.patterns;
public class GamePrototypeTest {
    public static void main(String[] args) {
        GamePrototype a = new GamePrototype("game", 2);
        GamePrototype b = a.copy();
        b.setLabel("game-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
