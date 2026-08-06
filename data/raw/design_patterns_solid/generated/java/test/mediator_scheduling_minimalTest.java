package org.example.patterns;
public class SchedulingMediatorTest {
    public static void main(String[] args) {
        SchedulingMediator m = new SchedulingMediator();
        new SchedulingColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
