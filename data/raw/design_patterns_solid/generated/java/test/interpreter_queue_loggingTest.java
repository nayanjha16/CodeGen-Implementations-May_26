package org.example.patterns;
public class QueueInterpreterTest {
    public static void main(String[] args) {
        QueueInterpreter i = new QueueInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
