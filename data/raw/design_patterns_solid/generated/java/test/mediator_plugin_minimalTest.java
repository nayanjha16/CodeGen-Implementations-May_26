package org.example.patterns;
public class PluginMediatorTest {
    public static void main(String[] args) {
        PluginMediator m = new PluginMediator();
        new PluginColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
