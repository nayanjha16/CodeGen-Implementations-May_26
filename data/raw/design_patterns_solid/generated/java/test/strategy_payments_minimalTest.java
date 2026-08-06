package org.example.patterns;
public class PaymentsStrategyTest {
    public static void main(String[] args) {
        PaymentsContext ctx = new PaymentsContext(new PaymentsDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
