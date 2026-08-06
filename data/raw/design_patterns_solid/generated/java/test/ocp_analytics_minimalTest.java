package org.example.patterns;
public class AnalyticsOcpTest {
    public static void main(String[] args) {
        if (new AnalyticsPriceEngine(new AnalyticsTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
