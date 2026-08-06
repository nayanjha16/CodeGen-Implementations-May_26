package org.example.patterns;
public class ReportAdapterTest {
    public static void main(String[] args) {
        ReportTarget t = new ReportAdapter(new ReportLegacyApi());
        if (!t.fetch().equals("modern-report")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
