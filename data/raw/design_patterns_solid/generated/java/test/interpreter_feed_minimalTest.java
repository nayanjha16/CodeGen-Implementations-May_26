package org.example.patterns;
public class FeedInterpreterTest {
    public static void main(String[] args) {
        FeedInterpreter i = new FeedInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
