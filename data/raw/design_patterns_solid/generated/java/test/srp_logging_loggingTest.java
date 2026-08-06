package org.example.patterns;
public class LoggingSrpTest {
    public static void main(String[] args) {
        LoggingRecord r = new LoggingRecord("a", 3);
        if (!new LoggingFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
