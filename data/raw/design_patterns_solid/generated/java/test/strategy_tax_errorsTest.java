package org.example.patterns;
public class TaxStrategyTest {
    public static void main(String[] args) {
        TaxContext ctx = new TaxContext(new TaxDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
