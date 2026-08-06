package org.example.patterns;
public class SchedulingChainTest {
    public static void main(String[] args) {
        SchedulingHandler h = new SchedulingLowHandler();
        h.link(new SchedulingHighHandler());
        if (!h.handle(2, "m").equals("high-scheduling:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
