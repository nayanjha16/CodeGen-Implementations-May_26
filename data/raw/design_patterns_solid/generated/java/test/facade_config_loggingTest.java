package org.example.patterns;
public class ConfigFacadeTest {
    public static void main(String[] args) {
        ConfigFacade f = new ConfigFacade();
        if (!f.submit("x").equals("wrote-config:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
