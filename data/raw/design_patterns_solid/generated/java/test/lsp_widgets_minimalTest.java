package org.example.patterns;
public class WidgetsLspTest {
    public static void main(String[] args) {
        WidgetsShape[] arr = new WidgetsShape[] { new WidgetsRectangle(2,3), new WidgetsSquare(4) };
        if (WidgetsLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
