package org.example.patterns;
public class ShippingCompositeTest {
    public static void main(String[] args) {
        ShippingComposite root = new ShippingComposite();
        root.add(new ShippingLeaf(2));
        root.add(new ShippingLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
