package org.example.patterns;
public class BackupMementoTest {
    public static void main(String[] args) {
        BackupOriginator o = new BackupOriginator();
        BackupMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("backup-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
