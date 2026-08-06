package org.example.patterns;
public class NotificationsOcpTest {
    public static void main(String[] args) {
        if (new NotificationsPriceEngine(new NotificationsTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
