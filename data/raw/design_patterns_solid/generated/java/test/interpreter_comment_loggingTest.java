package org.example.patterns;
public class CommentInterpreterTest {
    public static void main(String[] args) {
        CommentInterpreter i = new CommentInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
