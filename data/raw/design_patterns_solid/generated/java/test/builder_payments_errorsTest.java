package org.example.patterns;
public class PaymentsBuilderTest {
    public static void main(String[] args) {
        PaymentsConfig cfg = new PaymentsConfig.Builder().name("payments-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("payments-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
