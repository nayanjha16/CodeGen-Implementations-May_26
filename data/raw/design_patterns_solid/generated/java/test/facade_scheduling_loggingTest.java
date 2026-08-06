package org.example.patterns;
public class SchedulingFacadeTest {
    public static void main(String[] args) {
        SchedulingFacade f = new SchedulingFacade();
        if (!f.submit("x").equals("wrote-scheduling:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
