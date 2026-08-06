package org.example.patterns;
public class LoggingStateTest {
    public static void main(String[] args) {
        LoggingContext ctx = new LoggingContext();
        if (!ctx.request().equals("was-off-logging")) throw new AssertionError();
        if (!ctx.request().equals("was-on-logging")) throw new AssertionError();
        System.out.println("ok");
    }
}
