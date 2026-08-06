package org.example.patterns;
public class WalletOcpTest {
    public static void main(String[] args) {
        if (new WalletPriceEngine(new WalletTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
