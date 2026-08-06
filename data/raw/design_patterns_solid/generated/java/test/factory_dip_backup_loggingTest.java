package org.example.patterns;
public class BackupFactoryTest {
    public static void main(String[] args) {
        BackupFactory f = new BackupFactory();
        if (!f.create("basic").operate().equals("basic-backup")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-backup")) throw new AssertionError();
        System.out.println("ok");
    }
}
