package org.example.patterns;
public class NotificationsDecoratorTest {
    public static void main(String[] args) {
        NotificationsComponent c = new NotificationsUpperDecorator(new NotificationsCore());
        String out = c.process("ab");
        if (!out.equals("NOTIFICATIONS:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
