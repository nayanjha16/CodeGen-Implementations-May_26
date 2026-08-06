package org.example.patterns;
public class GameMediatorTest {
    public static void main(String[] args) {
        GameMediator m = new GameMediator();
        new GameColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
