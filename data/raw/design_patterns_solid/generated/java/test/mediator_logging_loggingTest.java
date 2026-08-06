package org.example.patterns;
public class LoggingMediatorTest {
    public static void main(String[] args) {
        LoggingMediator m = new LoggingMediator();
        new LoggingColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
