package org.example.patterns;
public class BackupAbstractFactoryTest {
    public static void main(String[] args) {
        String out = BackupAbstractFactoryDemo.run(new BackupCloudFactory());
        if (!out.equals("cloud-btn-backup|cloud-dlg-backup")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
