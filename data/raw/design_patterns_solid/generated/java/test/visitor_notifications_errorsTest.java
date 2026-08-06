package org.example.patterns;
public class NotificationsVisitorTest {
    public static void main(String[] args) {
        String out = new NotificationsLeaf("n").accept(new NotificationsPrintVisitor());
        if (!out.equals("notifications:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
