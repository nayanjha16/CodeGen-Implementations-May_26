package org.example.patterns;
public class WalletCommandTest {
    public static void main(String[] args) {
        WalletCommand cmd = new WalletActionCommand(new WalletReceiver(), "x");
        if (!cmd.execute().equals("done-wallet:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
