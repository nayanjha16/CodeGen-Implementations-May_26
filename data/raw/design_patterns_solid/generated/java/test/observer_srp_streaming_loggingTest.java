package org.example.patterns;
public class StreamingObserverTest {
    public static void main(String[] args) {
        StreamingSubject s = new StreamingSubject();
        StreamingListener l = new StreamingListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("streaming:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
