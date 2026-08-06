package org.example.patterns;
public class NotificationsDipTest {
    public static void main(String[] args) {
        String out = new NotificationsAppService(new NotificationsHttpGateway()).publish("p");
        if (!out.equals("http-notifications:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
