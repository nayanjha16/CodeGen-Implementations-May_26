package org.example.patterns;
public class PluginFacadeTest {
    public static void main(String[] args) {
        PluginFacade f = new PluginFacade();
        if (!f.submit("x").equals("wrote-plugin:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
