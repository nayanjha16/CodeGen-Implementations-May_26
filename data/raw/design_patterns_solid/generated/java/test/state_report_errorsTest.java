package org.example.patterns;
public class ReportStateTest {
    public static void main(String[] args) {
        ReportContext ctx = new ReportContext();
        if (!ctx.request().equals("was-off-report")) throw new AssertionError();
        if (!ctx.request().equals("was-on-report")) throw new AssertionError();
        System.out.println("ok");
    }
}
