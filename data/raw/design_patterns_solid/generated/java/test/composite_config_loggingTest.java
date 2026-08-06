package org.example.patterns;
public class ConfigCompositeTest {
    public static void main(String[] args) {
        ConfigComposite root = new ConfigComposite();
        root.add(new ConfigLeaf(2));
        root.add(new ConfigLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
