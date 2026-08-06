package org.example.patterns;
public class WalletLspTest {
    public static void main(String[] args) {
        WalletShape[] arr = new WalletShape[] { new WalletRectangle(2,3), new WalletSquare(4) };
        if (WalletLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
