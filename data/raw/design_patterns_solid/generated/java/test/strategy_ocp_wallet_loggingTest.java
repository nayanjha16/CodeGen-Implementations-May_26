package org.example.patterns;
public class WalletStrategyTest {
    public static void main(String[] args) {
        WalletContext ctx = new WalletContext(new WalletDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
