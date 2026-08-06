package org.example.patterns;
public class DiscountSingletonTest {
    public static void main(String[] args) {
        DiscountSingleton a = DiscountSingleton.getInstance();
        DiscountSingleton b = DiscountSingleton.getInstance();
        a.setValue("discount-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("discount-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
