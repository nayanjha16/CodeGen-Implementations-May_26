package org.example.patterns;
public class PluginFactoryTest {
    public static void main(String[] args) {
        PluginFactory f = new PluginFactory();
        if (!f.create("basic").operate().equals("basic-plugin")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-plugin")) throw new AssertionError();
        System.out.println("ok");
    }
}
