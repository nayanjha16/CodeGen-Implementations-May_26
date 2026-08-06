package org.example.patterns;
public class PluginCommandTest {
    public static void main(String[] args) {
        PluginCommand cmd = new PluginActionCommand(new PluginReceiver(), "x");
        if (!cmd.execute().equals("done-plugin:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
