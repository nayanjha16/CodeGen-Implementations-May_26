package org.example.patterns;
public class SyncBuilderTest {
    public static void main(String[] args) {
        SyncConfig cfg = new SyncConfig.Builder().name("sync-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("sync-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
