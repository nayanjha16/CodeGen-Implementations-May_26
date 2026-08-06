package org.example.patterns;
public class DiscountCompositeTest {
    public static void main(String[] args) {
        DiscountComposite root = new DiscountComposite();
        root.add(new DiscountLeaf(2));
        root.add(new DiscountLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
