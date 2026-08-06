package org.example.patterns;
public class ConfigChainTest {
    public static void main(String[] args) {
        ConfigHandler h = new ConfigLowHandler();
        h.link(new ConfigHighHandler());
        if (!h.handle(2, "m").equals("high-config:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
