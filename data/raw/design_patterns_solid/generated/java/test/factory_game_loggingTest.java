package org.example.patterns;
public class GameFactoryTest {
    public static void main(String[] args) {
        GameFactory f = new GameFactory();
        if (!f.create("basic").operate().equals("basic-game")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-game")) throw new AssertionError();
        System.out.println("ok");
    }
}
