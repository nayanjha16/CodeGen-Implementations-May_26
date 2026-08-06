package org.example.patterns;
public class SessionSrpTest {
    public static void main(String[] args) {
        SessionRecord r = new SessionRecord("a", 3);
        if (!new SessionFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
