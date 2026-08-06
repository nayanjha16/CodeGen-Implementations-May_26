package org.example.patterns;
public class WalletSingletonTest {
    public static void main(String[] args) {
        WalletSingleton a = WalletSingleton.getInstance();
        WalletSingleton b = WalletSingleton.getInstance();
        a.setValue("wallet-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("wallet-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
