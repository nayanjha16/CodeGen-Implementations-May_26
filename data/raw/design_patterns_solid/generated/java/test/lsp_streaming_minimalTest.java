package org.example.patterns;
public class StreamingLspTest {
    public static void main(String[] args) {
        StreamingShape[] arr = new StreamingShape[] { new StreamingRectangle(2,3), new StreamingSquare(4) };
        if (StreamingLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
