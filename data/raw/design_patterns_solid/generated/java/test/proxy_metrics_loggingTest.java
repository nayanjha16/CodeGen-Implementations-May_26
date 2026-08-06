package org.example.patterns;
public class MetricsProxyTest {
    public static void main(String[] args) {
        if (!new MetricsProxy(true).load("1").equals("real-metrics:1")) throw new AssertionError();
        if (!new MetricsProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
