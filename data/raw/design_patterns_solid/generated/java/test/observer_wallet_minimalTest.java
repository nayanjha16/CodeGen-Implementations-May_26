package org.example.patterns;
public class WalletObserverTest {
    public static void main(String[] args) {
        WalletSubject s = new WalletSubject();
        WalletListener l = new WalletListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("wallet:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
