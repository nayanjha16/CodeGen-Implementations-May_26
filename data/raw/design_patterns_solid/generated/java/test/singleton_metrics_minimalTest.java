package org.example.patterns;
public class MetricsSingletonTest {
    public static void main(String[] args) {
        MetricsSingleton a = MetricsSingleton.getInstance();
        MetricsSingleton b = MetricsSingleton.getInstance();
        a.setValue("metrics-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("metrics-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
