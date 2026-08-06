package org.example.patterns;
public class PluginSingletonTest {
    public static void main(String[] args) {
        PluginSingleton a = PluginSingleton.getInstance();
        PluginSingleton b = PluginSingleton.getInstance();
        a.setValue("plugin-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("plugin-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
