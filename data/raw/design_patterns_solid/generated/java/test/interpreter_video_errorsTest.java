package org.example.patterns;
public class VideoInterpreterTest {
    public static void main(String[] args) {
        VideoInterpreter i = new VideoInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
