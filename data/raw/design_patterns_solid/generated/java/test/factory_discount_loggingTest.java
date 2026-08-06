package org.example.patterns;
public class DiscountFactoryTest {
    public static void main(String[] args) {
        DiscountFactory f = new DiscountFactory();
        if (!f.create("basic").operate().equals("basic-discount")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-discount")) throw new AssertionError();
        System.out.println("ok");
    }
}
