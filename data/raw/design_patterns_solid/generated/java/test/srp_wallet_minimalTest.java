package org.example.patterns;
public class WalletSrpTest {
    public static void main(String[] args) {
        WalletRecord r = new WalletRecord("a", 3);
        if (!new WalletFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
