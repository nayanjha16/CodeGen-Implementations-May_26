package org.example.patterns;
public class PaymentsOcpTest {
    public static void main(String[] args) {
        if (new PaymentsPriceEngine(new PaymentsTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}
