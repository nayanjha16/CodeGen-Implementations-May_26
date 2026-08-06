package org.example.patterns;
public class BillingAdapterTest {
    public static void main(String[] args) {
        BillingTarget t = new BillingAdapter(new BillingLegacyApi());
        if (!t.fetch().equals("modern-billing")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
