package org.example.patterns;
public class EmailPrototypeTest {
    public static void main(String[] args) {
        EmailPrototype a = new EmailPrototype("email", 2);
        EmailPrototype b = a.copy();
        b.setLabel("email-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
