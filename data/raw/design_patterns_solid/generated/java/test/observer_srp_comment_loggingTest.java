package org.example.patterns;
public class CommentObserverTest {
    public static void main(String[] args) {
        CommentSubject s = new CommentSubject();
        CommentListener l = new CommentListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("comment:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
