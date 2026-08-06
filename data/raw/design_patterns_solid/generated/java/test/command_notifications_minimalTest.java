package org.example.patterns;
public class NotificationsCommandTest {
    public static void main(String[] args) {
        NotificationsCommand cmd = new NotificationsActionCommand(new NotificationsReceiver(), "x");
        if (!cmd.execute().equals("done-notifications:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
