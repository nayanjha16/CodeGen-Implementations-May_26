package org.example.patterns;
public class SessionBuilderTest {
    public static void main(String[] args) {
        SessionConfig cfg = new SessionConfig.Builder().name("session-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("session-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
