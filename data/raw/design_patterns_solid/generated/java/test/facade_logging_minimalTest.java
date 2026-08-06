package org.example.patterns;
public class LoggingFacadeTest {
    public static void main(String[] args) {
        LoggingFacade f = new LoggingFacade();
        if (!f.submit("x").equals("wrote-logging:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
