package org.example.patterns;
public class NotificationsStateTest {
    public static void main(String[] args) {
        NotificationsContext ctx = new NotificationsContext();
        if (!ctx.request().equals("was-off-notifications")) throw new AssertionError();
        if (!ctx.request().equals("was-on-notifications")) throw new AssertionError();
        System.out.println("ok");
    }
}
