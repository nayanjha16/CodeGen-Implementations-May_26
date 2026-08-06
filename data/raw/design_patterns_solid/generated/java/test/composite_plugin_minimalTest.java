package org.example.patterns;
public class PluginCompositeTest {
    public static void main(String[] args) {
        PluginComposite root = new PluginComposite();
        root.add(new PluginLeaf(2));
        root.add(new PluginLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
