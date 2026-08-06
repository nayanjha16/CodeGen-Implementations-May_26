package org.example.patterns;
public class SessionCommandTest {
    public static void main(String[] args) {
        SessionCommand cmd = new SessionActionCommand(new SessionReceiver(), "x");
        if (!cmd.execute().equals("done-session:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
