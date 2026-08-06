package org.example.patterns;
public class SearchObserverTest {
    public static void main(String[] args) {
        SearchSubject s = new SearchSubject();
        SearchListener l = new SearchListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("search:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
