package org.example.patterns;
public class HttpObserverTest {
    public static void main(String[] args) {
        HttpSubject s = new HttpSubject();
        HttpListener l = new HttpListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("http:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
