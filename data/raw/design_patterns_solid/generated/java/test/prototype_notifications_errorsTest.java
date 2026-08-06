package org.example.patterns;
public class NotificationsPrototypeTest {
    public static void main(String[] args) {
        NotificationsPrototype a = new NotificationsPrototype("notifications", 2);
        NotificationsPrototype b = a.copy();
        b.setLabel("notifications-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
