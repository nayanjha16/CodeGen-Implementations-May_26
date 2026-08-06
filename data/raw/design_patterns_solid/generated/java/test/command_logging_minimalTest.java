package org.example.patterns;
public class LoggingCommandTest {
    public static void main(String[] args) {
        LoggingCommand cmd = new LoggingActionCommand(new LoggingReceiver(), "x");
        if (!cmd.execute().equals("done-logging:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
