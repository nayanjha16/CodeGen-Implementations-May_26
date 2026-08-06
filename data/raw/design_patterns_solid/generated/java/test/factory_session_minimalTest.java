package org.example.patterns;
public class SessionFactoryTest {
    public static void main(String[] args) {
        SessionFactory f = new SessionFactory();
        if (!f.create("basic").operate().equals("basic-session")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-session")) throw new AssertionError();
        System.out.println("ok");
    }
}
