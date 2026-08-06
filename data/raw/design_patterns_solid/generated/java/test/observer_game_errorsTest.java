package org.example.patterns;
public class GameObserverTest {
    public static void main(String[] args) {
        GameSubject s = new GameSubject();
        GameListener l = new GameListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("game:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
