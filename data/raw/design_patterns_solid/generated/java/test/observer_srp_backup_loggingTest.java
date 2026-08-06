package org.example.patterns;
public class BackupObserverTest {
    public static void main(String[] args) {
        BackupSubject s = new BackupSubject();
        BackupListener l = new BackupListener();
        s.attach(l);
        s.notifyAllObservers("e");
        if (!l.last.equals("backup:e")) throw new AssertionError();
        System.out.println("ok");
    }
}
