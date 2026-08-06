package org.example.patterns;
public class CartSingletonTest {
    public static void main(String[] args) {
        CartSingleton a = CartSingleton.getInstance();
        CartSingleton b = CartSingleton.getInstance();
        a.setValue("cart-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("cart-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
