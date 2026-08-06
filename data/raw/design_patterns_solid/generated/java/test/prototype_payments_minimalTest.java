package org.example.patterns;
public class PaymentsPrototypeTest {
    public static void main(String[] args) {
        PaymentsPrototype a = new PaymentsPrototype("payments", 2);
        PaymentsPrototype b = a.copy();
        b.setLabel("payments-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
