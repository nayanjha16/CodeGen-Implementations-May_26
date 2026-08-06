package org.example.patterns;
public class AnalyticsAdapterTest {
    public static void main(String[] args) {
        AnalyticsTarget t = new AnalyticsAdapter(new AnalyticsLegacyApi());
        if (!t.fetch().equals("modern-analytics")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
