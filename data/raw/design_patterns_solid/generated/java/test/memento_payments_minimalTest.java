package org.example.patterns;
public class PaymentsMementoTest {
    public static void main(String[] args) {
        PaymentsOriginator o = new PaymentsOriginator();
        PaymentsMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("payments-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
