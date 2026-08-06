package org.example.patterns;
public class DatabaseCompositeTest {
    public static void main(String[] args) {
        DatabaseComposite root = new DatabaseComposite();
        root.add(new DatabaseLeaf(2));
        root.add(new DatabaseLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
