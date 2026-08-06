package org.example.patterns;
public class ReportStrategyTest {
    public static void main(String[] args) {
        ReportContext ctx = new ReportContext(new ReportDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
