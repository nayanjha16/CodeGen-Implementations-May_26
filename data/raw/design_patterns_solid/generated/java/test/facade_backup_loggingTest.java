package org.example.patterns;
public class BackupFacadeTest {
    public static void main(String[] args) {
        BackupFacade f = new BackupFacade();
        if (!f.submit("x").equals("wrote-backup:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
