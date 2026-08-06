package org.example.patterns;
public class NotificationsTemplateTest {
    public static void main(String[] args) {
        String out = new NotificationsUpperTemplate().run(" ab ");
        if (!out.equals("notifications|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
