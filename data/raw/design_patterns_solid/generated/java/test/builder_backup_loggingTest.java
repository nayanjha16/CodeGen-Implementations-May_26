package org.example.patterns;
public class BackupBuilderTest {
    public static void main(String[] args) {
        BackupConfig cfg = new BackupConfig.Builder().name("backup-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("backup-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
