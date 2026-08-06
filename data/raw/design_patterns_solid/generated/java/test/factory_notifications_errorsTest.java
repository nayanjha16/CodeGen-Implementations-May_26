package org.example.patterns;
public class NotificationsFactoryTest {
    public static void main(String[] args) {
        NotificationsFactory f = new NotificationsFactory();
        if (!f.create("basic").operate().equals("basic-notifications")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-notifications")) throw new AssertionError();
        System.out.println("ok");
    }
}
