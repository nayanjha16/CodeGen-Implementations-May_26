package org.example.patterns;
public class MapCompositeTest {
    public static void main(String[] args) {
        MapComposite root = new MapComposite();
        root.add(new MapLeaf(2));
        root.add(new MapLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
