package org.example.patterns;
public class SessionSingletonTest {
    public static void main(String[] args) {
        SessionSingleton a = SessionSingleton.getInstance();
        SessionSingleton b = SessionSingleton.getInstance();
        a.setValue("session-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("session-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
