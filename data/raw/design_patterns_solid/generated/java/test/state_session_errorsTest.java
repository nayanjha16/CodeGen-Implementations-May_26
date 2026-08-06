package org.example.patterns;
public class SessionStateTest {
    public static void main(String[] args) {
        SessionContext ctx = new SessionContext();
        if (!ctx.request().equals("was-off-session")) throw new AssertionError();
        if (!ctx.request().equals("was-on-session")) throw new AssertionError();
        System.out.println("ok");
    }
}
