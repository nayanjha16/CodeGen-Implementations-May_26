package org.example.patterns;
public class AudioObserverTest {
    public static void main(String[] args) {
        AudioSubject s = new AudioSubject();
        AudioListener l = new AudioListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("audio:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
