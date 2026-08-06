package org.example.patterns;
public class AnalyticsSingletonTest {
    public static void main(String[] args) {
        AnalyticsSingleton a = AnalyticsSingleton.getInstance();
        AnalyticsSingleton b = AnalyticsSingleton.getInstance();
        a.setValue("analytics-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("analytics-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
