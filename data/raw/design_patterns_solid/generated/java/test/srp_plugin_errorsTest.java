package org.example.patterns;
public class PluginSrpTest {
    public static void main(String[] args) {
        PluginRecord r = new PluginRecord("a", 3);
        if (!new PluginFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
