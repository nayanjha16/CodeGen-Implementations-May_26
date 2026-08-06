package org.example.patterns;
public class AnalyticsMediatorTest {
    public static void main(String[] args) {
        AnalyticsMediator m = new AnalyticsMediator();
        new AnalyticsColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
