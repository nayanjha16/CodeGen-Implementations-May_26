package org.example.patterns;
public class TaxLspTest {
    public static void main(String[] args) {
        TaxShape[] arr = new TaxShape[] { new TaxRectangle(2,3), new TaxSquare(4) };
        if (TaxLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
