package org.example.patterns;
public class HttpCompositeTest {
    public static void main(String[] args) {
        HttpComposite root = new HttpComposite();
        root.add(new HttpLeaf(2));
        root.add(new HttpLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
