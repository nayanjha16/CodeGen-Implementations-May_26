package org.example.patterns;
public class PluginLspTest {
    public static void main(String[] args) {
        PluginShape[] arr = new PluginShape[] { new PluginRectangle(2,3), new PluginSquare(4) };
        if (PluginLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
