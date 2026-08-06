package org.example.patterns;
public class SchedulingFactoryTest {
    public static void main(String[] args) {
        SchedulingFactory f = new SchedulingFactory();
        if (!f.create("basic").operate().equals("basic-scheduling")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-scheduling")) throw new AssertionError();
        System.out.println("ok");
    }
}
