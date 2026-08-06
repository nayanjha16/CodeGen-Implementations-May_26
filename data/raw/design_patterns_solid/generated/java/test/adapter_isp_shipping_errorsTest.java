package org.example.patterns;
public class ShippingAdapterTest {
    public static void main(String[] args) {
        ShippingTarget t = new ShippingAdapter(new ShippingLegacyApi());
        if (!t.fetch().equals("modern-shipping")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
