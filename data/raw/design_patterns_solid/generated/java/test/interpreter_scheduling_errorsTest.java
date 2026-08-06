package org.example.patterns;
public class SchedulingInterpreterTest {
    public static void main(String[] args) {
        SchedulingInterpreter i = new SchedulingInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
