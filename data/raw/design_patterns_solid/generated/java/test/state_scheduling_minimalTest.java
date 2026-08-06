package org.example.patterns;
public class SchedulingStateTest {
    public static void main(String[] args) {
        SchedulingContext ctx = new SchedulingContext();
        if (!ctx.request().equals("was-off-scheduling")) throw new AssertionError();
        if (!ctx.request().equals("was-on-scheduling")) throw new AssertionError();
        System.out.println("ok");
    }
}
