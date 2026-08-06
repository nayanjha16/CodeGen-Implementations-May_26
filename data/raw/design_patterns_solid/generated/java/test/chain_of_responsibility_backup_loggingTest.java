package org.example.patterns;
public class BackupChainTest {
    public static void main(String[] args) {
        BackupHandler h = new BackupLowHandler();
        h.link(new BackupHighHandler());
        if (!h.handle(2, "m").equals("high-backup:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
