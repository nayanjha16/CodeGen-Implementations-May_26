package org.example.patterns;
public class ReportOcpTest {
    public static void main(String[] args) {
        if (new ReportPriceEngine(new ReportTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
