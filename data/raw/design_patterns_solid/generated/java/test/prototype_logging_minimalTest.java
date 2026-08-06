package org.example.patterns;
public class LoggingPrototypeTest {
    public static void main(String[] args) {
        LoggingPrototype a = new LoggingPrototype("logging", 2);
        LoggingPrototype b = a.copy();
        b.setLabel("logging-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
