package org.example.patterns;
public class AnalyticsMementoTest {
    public static void main(String[] args) {
        AnalyticsOriginator o = new AnalyticsOriginator();
        AnalyticsMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("analytics-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
