package org.example.patterns;
public class WalletPrototypeTest {
    public static void main(String[] args) {
        WalletPrototype a = new WalletPrototype("wallet", 2);
        WalletPrototype b = a.copy();
        b.setLabel("wallet-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
