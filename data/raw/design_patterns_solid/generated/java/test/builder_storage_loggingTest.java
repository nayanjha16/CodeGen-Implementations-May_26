package org.example.patterns;
public class StorageBuilderTest {
    public static void main(String[] args) {
        StorageConfig cfg = new StorageConfig.Builder().name("storage-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("storage-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
