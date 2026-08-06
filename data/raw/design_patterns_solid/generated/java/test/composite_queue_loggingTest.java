package org.example.patterns;
public class QueueCompositeTest {
    public static void main(String[] args) {
        QueueComposite root = new QueueComposite();
        root.add(new QueueLeaf(2));
        root.add(new QueueLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
