package org.example.patterns;
public class EmailStateTest {
    public static void main(String[] args) {
        EmailContext ctx = new EmailContext();
        if (!ctx.request().equals("was-off-email")) throw new AssertionError();
        if (!ctx.request().equals("was-on-email")) throw new AssertionError();
        System.out.println("ok");
    }
}
