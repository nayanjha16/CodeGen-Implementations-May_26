package org.example.patterns;
public class ChatCompositeTest {
    public static void main(String[] args) {
        ChatComposite root = new ChatComposite();
        root.add(new ChatLeaf(2));
        root.add(new ChatLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
