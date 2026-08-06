package org.example.patterns;
public class LoggingOcpTest {
    public static void main(String[] args) {
        if (new LoggingPriceEngine(new LoggingTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
