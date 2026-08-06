package org.example.patterns;
public class ReportLspTest {
    public static void main(String[] args) {
        ReportShape[] arr = new ReportShape[] { new ReportRectangle(2,3), new ReportSquare(4) };
        if (ReportLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
