package org.example.patterns;
public class ConfigFactoryTest {
    public static void main(String[] args) {
        ConfigFactory f = new ConfigFactory();
        if (!f.create("basic").operate().equals("basic-config")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-config")) throw new AssertionError();
        System.out.println("ok");
    }
}
