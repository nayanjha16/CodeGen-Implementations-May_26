package org.example.patterns;
public class NotificationsMediatorTest {
    public static void main(String[] args) {
        NotificationsMediator m = new NotificationsMediator();
        new NotificationsColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
