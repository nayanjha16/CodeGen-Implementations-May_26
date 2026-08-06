package org.example.patterns;
public class WidgetsCommandTest {
    public static void main(String[] args) {
        WidgetsCommand cmd = new WidgetsActionCommand(new WidgetsReceiver(), "x");
        if (!cmd.execute().equals("done-widgets:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
