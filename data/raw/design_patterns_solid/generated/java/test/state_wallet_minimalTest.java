package org.example.patterns;
public class WalletStateTest {
    public static void main(String[] args) {
        WalletContext ctx = new WalletContext();
        if (!ctx.request().equals("was-off-wallet")) throw new AssertionError();
        if (!ctx.request().equals("was-on-wallet")) throw new AssertionError();
        System.out.println("ok");
    }
}
