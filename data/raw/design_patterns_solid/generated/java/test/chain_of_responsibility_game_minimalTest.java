package org.example.patterns;
public class GameChainTest {
    public static void main(String[] args) {
        GameHandler h = new GameLowHandler();
        h.link(new GameHighHandler());
        if (!h.handle(2, "m").equals("high-game:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
