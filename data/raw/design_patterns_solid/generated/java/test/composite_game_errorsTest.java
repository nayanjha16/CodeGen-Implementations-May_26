package org.example.patterns;
public class GameCompositeTest {
    public static void main(String[] args) {
        GameComposite root = new GameComposite();
        root.add(new GameLeaf(2));
        root.add(new GameLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
