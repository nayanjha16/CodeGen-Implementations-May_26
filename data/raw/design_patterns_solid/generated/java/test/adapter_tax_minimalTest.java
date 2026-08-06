package org.example.patterns;
public class TaxAdapterTest {
    public static void main(String[] args) {
        TaxTarget t = new TaxAdapter(new TaxLegacyApi());
        if (!t.fetch().equals("modern-tax")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
