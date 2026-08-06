package org.example.patterns;
public class SessionMediatorTest {
    public static void main(String[] args) {
        SessionMediator m = new SessionMediator();
        new SessionColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
