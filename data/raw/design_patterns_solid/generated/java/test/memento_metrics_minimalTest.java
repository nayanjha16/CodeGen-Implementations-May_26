package org.example.patterns;
public class MetricsMementoTest {
    public static void main(String[] args) {
        MetricsOriginator o = new MetricsOriginator();
        MetricsMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("metrics-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
