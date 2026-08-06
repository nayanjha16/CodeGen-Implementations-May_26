package org.example.patterns;
public class SchedulingCommandTest {
    public static void main(String[] args) {
        SchedulingCommand cmd = new SchedulingActionCommand(new SchedulingReceiver(), "x");
        if (!cmd.execute().equals("done-scheduling:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
