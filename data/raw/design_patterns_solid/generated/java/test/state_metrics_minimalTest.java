package org.example.patterns;
public class MetricsStateTest {
    public static void main(String[] args) {
        MetricsContext ctx = new MetricsContext();
        if (!ctx.request().equals("was-off-metrics")) throw new AssertionError();
        if (!ctx.request().equals("was-on-metrics")) throw new AssertionError();
        System.out.println("ok");
    }
}
