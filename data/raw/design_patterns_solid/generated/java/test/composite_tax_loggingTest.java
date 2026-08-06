package org.example.patterns;
public class TaxCompositeTest {
    public static void main(String[] args) {
        TaxComposite root = new TaxComposite();
        root.add(new TaxLeaf(2));
        root.add(new TaxLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
