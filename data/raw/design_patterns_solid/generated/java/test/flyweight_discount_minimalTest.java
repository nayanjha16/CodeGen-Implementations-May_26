package org.example.patterns;
public class DiscountFlyweightTest {
    public static void main(String[] args) {
        DiscountFlyweightFactory f = new DiscountFlyweightFactory();
        String a = f.intern("a");
        String b = f.intern("a");
        if (a != b) throw new AssertionError();
        if (f.size() != 1) throw new AssertionError();
        System.out.println("ok");
    }
}
