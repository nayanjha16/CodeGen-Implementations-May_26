package org.example.patterns;
public class EmailObserverTest {
    public static void main(String[] args) {
        EmailSubject s = new EmailSubject();
        EmailListener l = new EmailListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("email:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
