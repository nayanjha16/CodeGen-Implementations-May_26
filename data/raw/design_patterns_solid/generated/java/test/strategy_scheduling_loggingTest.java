package org.example.patterns;
public class SchedulingStrategyTest {
    public static void main(String[] args) {
        SchedulingContext ctx = new SchedulingContext(new SchedulingDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
