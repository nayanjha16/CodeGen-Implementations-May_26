package org.example.patterns;
public class MetricsOcpTest {
    public static void main(String[] args) {
        if (new MetricsPriceEngine(new MetricsTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
