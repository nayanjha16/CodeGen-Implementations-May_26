package org.example.patterns;
public class ConfigCommandTest {
    public static void main(String[] args) {
        ConfigCommand cmd = new ConfigActionCommand(new ConfigReceiver(), "x");
        if (!cmd.execute().equals("done-config:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
