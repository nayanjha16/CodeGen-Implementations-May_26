package org.example.patterns;
public class LoggingMementoTest {
    public static void main(String[] args) {
        LoggingOriginator o = new LoggingOriginator();
        LoggingMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("logging-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
