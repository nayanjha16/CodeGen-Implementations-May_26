package org.example.patterns;
public class SessionChainTest {
    public static void main(String[] args) {
        SessionHandler h = new SessionLowHandler();
        h.link(new SessionHighHandler());
        if (!h.handle(2, "m").equals("high-session:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
