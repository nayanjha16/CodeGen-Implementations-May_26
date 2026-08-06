package org.example.patterns;
public class DiscountAdapterTest {
    public static void main(String[] args) {
        DiscountTarget t = new DiscountAdapter(new DiscountLegacyApi());
        if (!t.fetch().equals("modern-discount")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
