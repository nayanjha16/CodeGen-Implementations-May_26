package org.example.patterns;
public class StreamingCommandTest {
    public static void main(String[] args) {
        StreamingCommand cmd = new StreamingActionCommand(new StreamingReceiver(), "x");
        if (!cmd.execute().equals("done-streaming:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
