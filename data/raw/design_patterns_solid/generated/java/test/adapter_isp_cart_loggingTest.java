package org.example.patterns;
public class CartAdapterTest {
    public static void main(String[] args) {
        CartTarget t = new CartAdapter(new CartLegacyApi());
        if (!t.fetch().equals("modern-cart")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
