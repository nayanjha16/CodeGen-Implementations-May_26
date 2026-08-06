package org.example.patterns;
public class SensorsLspTest {
    public static void main(String[] args) {
        SensorsShape[] arr = new SensorsShape[] { new SensorsRectangle(2,3), new SensorsSquare(4) };
        if (SensorsLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
