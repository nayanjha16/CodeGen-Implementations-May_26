package org.example.patterns;
public class LicenseBuilderTest {
    public static void main(String[] args) {
        LicenseConfig cfg = new LicenseConfig.Builder().name("license-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("license-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
