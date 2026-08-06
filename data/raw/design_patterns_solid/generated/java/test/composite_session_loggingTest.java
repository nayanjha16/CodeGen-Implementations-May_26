package org.example.patterns;
public class SessionCompositeTest {
    public static void main(String[] args) {
        SessionComposite root = new SessionComposite();
        root.add(new SessionLeaf(2));
        root.add(new SessionLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
