package org.example.patterns;
public class GameFacadeTest {
    public static void main(String[] args) {
        GameFacade f = new GameFacade();
        if (!f.submit("x").equals("wrote-game:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
