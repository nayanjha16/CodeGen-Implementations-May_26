package org.example.patterns;
public class BackupLspTest {
    public static void main(String[] args) {
        BackupShape[] arr = new BackupShape[] { new BackupRectangle(2,3), new BackupSquare(4) };
        if (BackupLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
