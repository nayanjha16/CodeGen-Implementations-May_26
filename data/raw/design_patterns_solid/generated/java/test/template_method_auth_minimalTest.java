package org.example.patterns;
public class AuthTemplateTest {
    public static void main(String[] args) {
        String out = new AuthUpperTemplate().run(" ab ");
        if (!out.equals("auth|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
