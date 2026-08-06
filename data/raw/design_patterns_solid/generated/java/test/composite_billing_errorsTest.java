package org.example.patterns;
public class BillingCompositeTest {
    public static void main(String[] args) {
        BillingComposite root = new BillingComposite();
        root.add(new BillingLeaf(2));
        root.add(new BillingLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
