package org.example.patterns;
public class AnalyticsPrototypeTest {
    public static void main(String[] args) {
        AnalyticsPrototype a = new AnalyticsPrototype("analytics", 2);
        AnalyticsPrototype b = a.copy();
        b.setLabel("analytics-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
