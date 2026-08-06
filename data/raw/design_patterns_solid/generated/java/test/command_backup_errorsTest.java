package org.example.patterns;
public class BackupCommandTest {
    public static void main(String[] args) {
        BackupCommand cmd = new BackupActionCommand(new BackupReceiver(), "x");
        if (!cmd.execute().equals("done-backup:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
