package org.example.patterns;
public class BillingSrpTest {
    public static void main(String[] args) {
        BillingRecord r = new BillingRecord("a", 3);
        if (!new BillingFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
