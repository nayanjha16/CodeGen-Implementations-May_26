package org.example.patterns;
public class LoggingChainTest {
    public static void main(String[] args) {
        LoggingHandler h = new LoggingLowHandler();
        h.link(new LoggingHighHandler());
        if (!h.handle(2, "m").equals("high-logging:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
