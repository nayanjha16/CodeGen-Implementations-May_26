package org.example.patterns;
public class WalletChainTest {
    public static void main(String[] args) {
        WalletHandler h = new WalletLowHandler();
        h.link(new WalletHighHandler());
        if (!h.handle(2, "m").equals("high-wallet:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
