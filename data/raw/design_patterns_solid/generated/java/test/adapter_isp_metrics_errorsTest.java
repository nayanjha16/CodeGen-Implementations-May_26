package org.example.patterns;
public class MetricsAdapterTest {
    public static void main(String[] args) {
        MetricsTarget t = new MetricsAdapter(new MetricsLegacyApi());
        if (!t.fetch().equals("modern-metrics")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
