package org.example.patterns;
public class ConfigObserverTest {
    public static void main(String[] args) {
        ConfigSubject s = new ConfigSubject();
        ConfigListener l = new ConfigListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("config:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
