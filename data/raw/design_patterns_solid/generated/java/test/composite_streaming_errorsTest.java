package org.example.patterns;
public class StreamingCompositeTest {
    public static void main(String[] args) {
        StreamingComposite root = new StreamingComposite();
        root.add(new StreamingLeaf(2));
        root.add(new StreamingLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
