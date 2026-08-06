package org.example.patterns;
public class BillingLspTest {
    public static void main(String[] args) {
        BillingShape[] arr = new BillingShape[] { new BillingRectangle(2,3), new BillingSquare(4) };
        if (BillingLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
