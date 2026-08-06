package org.example.patterns;
public class ConfigMediatorTest {
    public static void main(String[] args) {
        ConfigMediator m = new ConfigMediator();
        new ConfigColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
