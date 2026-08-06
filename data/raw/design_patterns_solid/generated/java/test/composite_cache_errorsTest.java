package org.example.patterns;
public class CacheCompositeTest {
    public static void main(String[] args) {
        CacheComposite root = new CacheComposite();
        root.add(new CacheLeaf(2));
        root.add(new CacheLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
