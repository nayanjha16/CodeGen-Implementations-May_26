package org.example.patterns;
public class SmsBuilderTest {
    public static void main(String[] args) {
        SmsConfig cfg = new SmsConfig.Builder().name("sms-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("sms-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
