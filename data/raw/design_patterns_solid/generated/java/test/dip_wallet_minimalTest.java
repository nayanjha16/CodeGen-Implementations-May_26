package org.example.patterns;
public class WalletDipTest {
    public static void main(String[] args) {
        String out = new WalletAppService(new WalletHttpGateway()).publish("p");
        if (!out.equals("http-wallet:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
