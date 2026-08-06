package org.example.patterns;
public class LoggingLspTest {
    public static void main(String[] args) {
        LoggingShape[] arr = new LoggingShape[] { new LoggingRectangle(2,3), new LoggingSquare(4) };
        if (LoggingLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
