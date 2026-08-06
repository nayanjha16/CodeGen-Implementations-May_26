package org.example.patterns;
public class SchedulingSrpTest {
    public static void main(String[] args) {
        SchedulingRecord r = new SchedulingRecord("a", 3);
        if (!new SchedulingFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
