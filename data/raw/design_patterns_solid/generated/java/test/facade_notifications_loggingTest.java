package org.example.patterns;
public class NotificationsFacadeTest {
    public static void main(String[] args) {
        NotificationsFacade f = new NotificationsFacade();
        if (!f.submit("x").equals("wrote-notifications:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
