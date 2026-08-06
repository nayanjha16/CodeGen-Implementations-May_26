package org.example.patterns;
public class MetricsCommandTest {
    public static void main(String[] args) {
        MetricsCommand cmd = new MetricsActionCommand(new MetricsReceiver(), "x");
        if (!cmd.execute().equals("done-metrics:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
