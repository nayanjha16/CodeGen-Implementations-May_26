package org.example.patterns;
public class MetricsSrpTest {
    public static void main(String[] args) {
        MetricsRecord r = new MetricsRecord("a", 3);
        if (!new MetricsFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
