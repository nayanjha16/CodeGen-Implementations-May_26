package org.example.patterns;
public class WalletCompositeTest {
    public static void main(String[] args) {
        WalletComposite root = new WalletComposite();
        root.add(new WalletLeaf(2));
        root.add(new WalletLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
