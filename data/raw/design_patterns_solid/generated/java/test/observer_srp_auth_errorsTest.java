package org.example.patterns;
public class AuthObserverTest {
    public static void main(String[] args) {
        AuthSubject s = new AuthSubject();
        AuthListener l = new AuthListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("auth:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
