package org.example.patterns;
public class WalletBuilderTest {
    public static void main(String[] args) {
        WalletConfig cfg = new WalletConfig.Builder().name("wallet-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("wallet-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
