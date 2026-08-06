package org.example.patterns;
public class PaymentsSrpTest {
    public static void main(String[] args) {
        PaymentsRecord r = new PaymentsRecord("a", 3);
        if (!new PaymentsFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
