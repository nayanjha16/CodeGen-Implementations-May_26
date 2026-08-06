package org.example.patterns;
public class AnalyticsTemplateTest {
    public static void main(String[] args) {
        String out = new AnalyticsUpperTemplate().run(" ab ");
        if (!out.equals("analytics|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
