package org.example.patterns;
public class AnalyticsCommandTest {
    public static void main(String[] args) {
        AnalyticsCommand cmd = new AnalyticsActionCommand(new AnalyticsReceiver(), "x");
        if (!cmd.execute().equals("done-analytics:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
