package org.example.patterns;
public class LoggingProxyTest {
    public static void main(String[] args) {
        if (!new LoggingProxy(true).load("1").equals("real-logging:1")) throw new AssertionError();
        if (!new LoggingProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
