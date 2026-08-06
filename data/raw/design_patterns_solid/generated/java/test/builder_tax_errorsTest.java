package org.example.patterns;
public class TaxBuilderTest {
    public static void main(String[] args) {
        TaxConfig cfg = new TaxConfig.Builder().name("tax-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("tax-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
