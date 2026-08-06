package org.example.patterns;
public class SchedulingLspTest {
    public static void main(String[] args) {
        SchedulingShape[] arr = new SchedulingShape[] { new SchedulingRectangle(2,3), new SchedulingSquare(4) };
        if (SchedulingLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
