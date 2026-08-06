package org.example.patterns;
public class WalletMediatorTest {
    public static void main(String[] args) {
        WalletMediator m = new WalletMediator();
        new WalletColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
