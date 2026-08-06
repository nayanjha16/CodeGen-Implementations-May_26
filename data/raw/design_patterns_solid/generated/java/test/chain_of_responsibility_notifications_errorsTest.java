package org.example.patterns;
public class NotificationsChainTest {
    public static void main(String[] args) {
        NotificationsHandler h = new NotificationsLowHandler();
        h.link(new NotificationsHighHandler());
        if (!h.handle(2, "m").equals("high-notifications:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
