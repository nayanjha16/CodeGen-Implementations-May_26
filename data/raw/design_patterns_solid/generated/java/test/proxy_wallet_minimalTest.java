package org.example.patterns;
public class WalletProxyTest {
    public static void main(String[] args) {
        if (!new WalletProxy(true).load("1").equals("real-wallet:1")) throw new AssertionError();
        if (!new WalletProxy(false).load("1").equals("denied")) throw new AssertionError();
        System.out.println("ok");
    }
}
