package org.example.patterns;
public class ConfigSingletonTest {
    public static void main(String[] args) {
        ConfigSingleton a = ConfigSingleton.getInstance();
        ConfigSingleton b = ConfigSingleton.getInstance();
        a.setValue("config-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("config-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
