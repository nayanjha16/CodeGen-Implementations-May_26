package org.example.patterns;
public class LoggingFactoryTest {
    public static void main(String[] args) {
        LoggingFactory f = new LoggingFactory();
        if (!f.create("basic").operate().equals("basic-logging")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-logging")) throw new AssertionError();
        System.out.println("ok");
    }
}
