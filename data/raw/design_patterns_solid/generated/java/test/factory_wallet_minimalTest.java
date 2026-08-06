package org.example.patterns;
public class WalletFactoryTest {
    public static void main(String[] args) {
        WalletFactory f = new WalletFactory();
        if (!f.create("basic").operate().equals("basic-wallet")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-wallet")) throw new AssertionError();
        System.out.println("ok");
    }
}
