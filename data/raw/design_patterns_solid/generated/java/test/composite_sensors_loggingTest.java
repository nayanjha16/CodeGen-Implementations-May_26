package org.example.patterns;
public class SensorsCompositeTest {
    public static void main(String[] args) {
        SensorsComposite root = new SensorsComposite();
        root.add(new SensorsLeaf(2));
        root.add(new SensorsLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
