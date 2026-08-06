package org.example.patterns;
public class MetricsFactoryTest {
    public static void main(String[] args) {
        MetricsFactory f = new MetricsFactory();
        if (!f.create("basic").operate().equals("basic-metrics")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-metrics")) throw new AssertionError();
        System.out.println("ok");
    }
}
