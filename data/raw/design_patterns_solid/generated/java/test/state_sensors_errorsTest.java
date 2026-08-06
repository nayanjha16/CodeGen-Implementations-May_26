package org.example.patterns;
public class SensorsStateTest {
    public static void main(String[] args) {
        SensorsContext ctx = new SensorsContext();
        if (!ctx.request().equals("was-off-sensors")) throw new AssertionError();
        if (!ctx.request().equals("was-on-sensors")) throw new AssertionError();
        System.out.println("ok");
    }
}
