package org.example.patterns;
public class VideoObserverTest {
    public static void main(String[] args) {
        VideoSubject s = new VideoSubject();
        VideoListener l = new VideoListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("video:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
