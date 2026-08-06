package org.example.patterns;
public class BillingStrategyTest {
    public static void main(String[] args) {
        BillingContext ctx = new BillingContext(new BillingDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
