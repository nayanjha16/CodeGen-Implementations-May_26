package org.example.patterns;
public class CartCompositeTest {
    public static void main(String[] args) {
        CartComposite root = new CartComposite();
        root.add(new CartLeaf(2));
        root.add(new CartLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
