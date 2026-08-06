package org.example.patterns;
public class SyncCommandTest {
    public static void main(String[] args) {
        SyncCommand cmd = new SyncActionCommand(new SyncReceiver(), "x");
        if (!cmd.execute().equals("done-sync:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
