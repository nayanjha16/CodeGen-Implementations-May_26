package org.example.patterns;
public class PluginVisitorTest {
    public static void main(String[] args) {
        String out = new PluginLeaf("n").accept(new PluginPrintVisitor());
        if (!out.equals("plugin:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
