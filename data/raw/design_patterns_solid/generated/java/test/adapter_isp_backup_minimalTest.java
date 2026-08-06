package org.example.patterns;
public class BackupAdapterTest {
    public static void main(String[] args) {
        BackupTarget t = new BackupAdapter(new BackupLegacyApi());
        if (!t.fetch().equals("modern-backup")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
