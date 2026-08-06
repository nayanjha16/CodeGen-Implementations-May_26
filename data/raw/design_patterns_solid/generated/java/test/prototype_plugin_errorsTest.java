package org.example.patterns;
public class PluginPrototypeTest {
    public static void main(String[] args) {
        PluginPrototype a = new PluginPrototype("plugin", 2);
        PluginPrototype b = a.copy();
        b.setLabel("plugin-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
