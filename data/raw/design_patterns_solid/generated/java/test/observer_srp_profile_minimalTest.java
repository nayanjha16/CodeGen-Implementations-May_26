package org.example.patterns;
public class ProfileObserverTest {
    public static void main(String[] args) {
        ProfileSubject s = new ProfileSubject();
        ProfileListener l = new ProfileListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("profile:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
