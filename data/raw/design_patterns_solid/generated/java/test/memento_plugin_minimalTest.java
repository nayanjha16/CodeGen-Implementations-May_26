package org.example.patterns;
public class PluginMementoTest {
    public static void main(String[] args) {
        PluginOriginator o = new PluginOriginator();
        PluginMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("plugin-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
