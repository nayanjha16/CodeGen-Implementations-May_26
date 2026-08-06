package org.example.patterns;
public class CanvasCompositeTest {
    public static void main(String[] args) {
        CanvasComposite root = new CanvasComposite();
        root.add(new CanvasLeaf(2));
        root.add(new CanvasLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
