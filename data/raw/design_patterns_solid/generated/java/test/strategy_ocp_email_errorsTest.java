package org.example.patterns;
public class EmailStrategyTest {
    public static void main(String[] args) {
        EmailContext ctx = new EmailContext(new EmailDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
