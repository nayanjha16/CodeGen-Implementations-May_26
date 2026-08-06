package org.example.patterns;
public class AuthMediatorTest {
    public static void main(String[] args) {
        AuthMediator m = new AuthMediator();
        new AuthColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
