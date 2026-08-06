package org.example.patterns;
public class QueueCommandTest {
    public static void main(String[] args) {
        QueueCommand cmd = new QueueActionCommand(new QueueReceiver(), "x");
        if (!cmd.execute().equals("done-queue:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
