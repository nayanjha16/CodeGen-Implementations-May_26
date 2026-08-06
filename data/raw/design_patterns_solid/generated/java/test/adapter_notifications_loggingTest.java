package org.example.patterns;
public class NotificationsAdapterTest {
    public static void main(String[] args) {
        NotificationsTarget t = new NotificationsAdapter(new NotificationsLegacyApi());
        if (!t.fetch().equals("modern-notifications")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
