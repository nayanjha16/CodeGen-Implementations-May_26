package org.example.patterns;
public class WalletMementoTest {
    public static void main(String[] args) {
        WalletOriginator o = new WalletOriginator();
        WalletMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("wallet-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
