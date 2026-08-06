package org.example.patterns;
public class PluginObserverTest {
    public static void main(String[] args) {
        PluginSubject s = new PluginSubject();
        PluginListener l = new PluginListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("plugin:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
