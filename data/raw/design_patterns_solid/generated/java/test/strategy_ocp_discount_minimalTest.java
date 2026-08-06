package org.example.patterns;
public class DiscountStrategyTest {
    public static void main(String[] args) {
        DiscountContext ctx = new DiscountContext(new DiscountDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
