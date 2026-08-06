package org.example.patterns;
public class NotificationsBuilderTest {
    public static void main(String[] args) {
        NotificationsConfig cfg = new NotificationsConfig.Builder().name("notifications-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("notifications-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
