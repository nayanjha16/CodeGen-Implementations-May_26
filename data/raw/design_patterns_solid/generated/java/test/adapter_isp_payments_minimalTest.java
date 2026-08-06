package org.example.patterns;
public class PaymentsAdapterTest {
    public static void main(String[] args) {
        PaymentsTarget t = new PaymentsAdapter(new PaymentsLegacyApi());
        if (!t.fetch().equals("modern-payments")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
