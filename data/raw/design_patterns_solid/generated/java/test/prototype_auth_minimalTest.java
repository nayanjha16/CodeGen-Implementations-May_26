package org.example.patterns;
public class AuthPrototypeTest {
    public static void main(String[] args) {
        AuthPrototype a = new AuthPrototype("auth", 2);
        AuthPrototype b = a.copy();
        b.setLabel("auth-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
