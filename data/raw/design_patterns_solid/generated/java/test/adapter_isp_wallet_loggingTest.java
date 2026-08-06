package org.example.patterns;
public class WalletAdapterTest {
    public static void main(String[] args) {
        WalletTarget t = new WalletAdapter(new WalletLegacyApi());
        if (!t.fetch().equals("modern-wallet")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
