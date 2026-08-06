package org.example.patterns;
public class ReportSingletonTest {
    public static void main(String[] args) {
        ReportSingleton a = ReportSingleton.getInstance();
        ReportSingleton b = ReportSingleton.getInstance();
        a.setValue("report-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("report-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
