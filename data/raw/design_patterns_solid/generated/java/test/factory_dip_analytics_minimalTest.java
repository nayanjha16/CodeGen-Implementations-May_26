package org.example.patterns;
public class AnalyticsFactoryTest {
    public static void main(String[] args) {
        AnalyticsFactory f = new AnalyticsFactory();
        if (!f.create("basic").operate().equals("basic-analytics")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-analytics")) throw new AssertionError();
        System.out.println("ok");
    }
}
