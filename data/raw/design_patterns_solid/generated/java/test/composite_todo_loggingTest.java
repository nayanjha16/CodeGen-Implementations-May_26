package org.example.patterns;
public class TodoCompositeTest {
    public static void main(String[] args) {
        TodoComposite root = new TodoComposite();
        root.add(new TodoLeaf(2));
        root.add(new TodoLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
