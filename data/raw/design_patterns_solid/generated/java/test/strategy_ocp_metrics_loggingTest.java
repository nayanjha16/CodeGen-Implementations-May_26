package org.example.patterns;
public class MetricsStrategyTest {
    public static void main(String[] args) {
        MetricsContext ctx = new MetricsContext(new MetricsDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
