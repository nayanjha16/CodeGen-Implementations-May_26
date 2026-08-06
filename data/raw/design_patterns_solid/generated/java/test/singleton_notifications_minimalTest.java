package org.example.patterns;
public class NotificationsSingletonTest {
    public static void main(String[] args) {
        NotificationsSingleton a = NotificationsSingleton.getInstance();
        NotificationsSingleton b = NotificationsSingleton.getInstance();
        a.setValue("notifications-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("notifications-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
