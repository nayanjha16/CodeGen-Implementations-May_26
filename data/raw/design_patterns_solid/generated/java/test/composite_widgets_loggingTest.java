package org.example.patterns;
public class WidgetsCompositeTest {
    public static void main(String[] args) {
        WidgetsComposite root = new WidgetsComposite();
        root.add(new WidgetsLeaf(2));
        root.add(new WidgetsLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
