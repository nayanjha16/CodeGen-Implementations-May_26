package org.example.patterns;
public class ChatObserverTest {
    public static void main(String[] args) {
        ChatSubject s = new ChatSubject();
        ChatListener l = new ChatListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("chat:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
