package org.example.patterns;
public class QueueBuilderTest {
    public static void main(String[] args) {
        QueueConfig cfg = new QueueConfig.Builder().name("queue-x").limit(3).enabled(false).build();
        if (!cfg.summary().equals("queue-x:3:false")) throw new AssertionError(cfg.summary());
        System.out.println("ok");
    }
}
