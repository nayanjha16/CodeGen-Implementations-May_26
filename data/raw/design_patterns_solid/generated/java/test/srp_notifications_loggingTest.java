package org.example.patterns;
public class NotificationsSrpTest {
    public static void main(String[] args) {
        NotificationsRecord r = new NotificationsRecord("a", 3);
        if (!new NotificationsFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
