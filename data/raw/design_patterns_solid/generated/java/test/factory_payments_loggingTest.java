package org.example.patterns;
public class PaymentsFactoryTest {
    public static void main(String[] args) {
        PaymentsFactory f = new PaymentsFactory();
        if (!f.create("basic").operate().equals("basic-payments")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-payments")) throw new AssertionError();
        System.out.println("ok");
    }
}
