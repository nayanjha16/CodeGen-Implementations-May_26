package org.example.patterns;
public class GameMementoTest {
    public static void main(String[] args) {
        GameOriginator o = new GameOriginator();
        GameMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("game-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
