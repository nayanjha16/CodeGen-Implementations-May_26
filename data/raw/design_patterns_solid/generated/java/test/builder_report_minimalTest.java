package org.example.patterns;
public class ReportBuilderTest {
    public static void main(String[] args) {
        ReportConfig cfg = new ReportConfig.Builder().name("report-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("report-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
