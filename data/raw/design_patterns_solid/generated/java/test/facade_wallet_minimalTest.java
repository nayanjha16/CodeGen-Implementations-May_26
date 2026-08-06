package org.example.patterns;
public class WalletFacadeTest {
    public static void main(String[] args) {
        WalletFacade f = new WalletFacade();
        if (!f.submit("x").equals("wrote-wallet:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
