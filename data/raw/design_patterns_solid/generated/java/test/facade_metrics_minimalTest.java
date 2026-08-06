package org.example.patterns;
public class MetricsFacadeTest {
    public static void main(String[] args) {
        MetricsFacade f = new MetricsFacade();
        if (!f.submit("x").equals("wrote-metrics:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
