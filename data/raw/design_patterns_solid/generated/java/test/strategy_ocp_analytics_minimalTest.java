package org.example.patterns;
public class AnalyticsStrategyTest {
    public static void main(String[] args) {
        AnalyticsContext ctx = new AnalyticsContext(new AnalyticsDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
