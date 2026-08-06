package org.example.patterns;
public class PaymentsSingletonTest {
    public static void main(String[] args) {
        PaymentsSingleton a = PaymentsSingleton.getInstance();
        PaymentsSingleton b = PaymentsSingleton.getInstance();
        a.setValue("payments-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("payments-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
