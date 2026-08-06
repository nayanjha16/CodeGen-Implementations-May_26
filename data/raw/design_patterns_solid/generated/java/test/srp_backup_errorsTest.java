package org.example.patterns;
public class BackupSrpTest {
    public static void main(String[] args) {
        BackupRecord r = new BackupRecord("a", 3);
        if (!new BackupFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
