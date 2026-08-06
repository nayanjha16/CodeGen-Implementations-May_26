package org.example.patterns;
public class EmailBuilderTest {
    public static void main(String[] args) {
        EmailConfig cfg = new EmailConfig.Builder().name("email-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("email-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
