package org.example.patterns;
public class MetricsChainTest {
    public static void main(String[] args) {
        MetricsHandler h = new MetricsLowHandler();
        h.link(new MetricsHighHandler());
        if (!h.handle(2, "m").equals("high-metrics:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
