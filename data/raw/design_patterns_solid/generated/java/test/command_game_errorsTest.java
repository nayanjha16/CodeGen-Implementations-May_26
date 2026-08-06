package org.example.patterns;
public class GameCommandTest {
    public static void main(String[] args) {
        GameCommand cmd = new GameActionCommand(new GameReceiver(), "x");
        if (!cmd.execute().equals("done-game:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
