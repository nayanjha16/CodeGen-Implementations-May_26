package org.example.patterns;
public class ReportSrpTest {
    public static void main(String[] args) {
        ReportRecord r = new ReportRecord("a", 3);
        if (!new ReportFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
