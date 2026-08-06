package org.example.patterns;
public class StreamingInterpreterTest {
    public static void main(String[] args) {
        StreamingInterpreter i = new StreamingInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
