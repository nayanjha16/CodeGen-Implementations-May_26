package org.example.patterns;
public class StorageCompositeTest {
    public static void main(String[] args) {
        StorageComposite root = new StorageComposite();
        root.add(new StorageLeaf(2));
        root.add(new StorageLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
