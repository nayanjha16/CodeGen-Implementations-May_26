package org.example.patterns;
public class NotificationsMementoTest {
    public static void main(String[] args) {
        NotificationsOriginator o = new NotificationsOriginator();
        NotificationsMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("notifications-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
