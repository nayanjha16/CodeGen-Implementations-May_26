package org.example.patterns;
public class DatabaseBuilderTest {
    public static void main(String[] args) {
        DatabaseConfig cfg = new DatabaseConfig.Builder().name("database-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("database-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
