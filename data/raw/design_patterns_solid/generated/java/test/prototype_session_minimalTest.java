package org.example.patterns;
public class SessionPrototypeTest {
    public static void main(String[] args) {
        SessionPrototype a = new SessionPrototype("session", 2);
        SessionPrototype b = a.copy();
        b.setLabel("session-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
