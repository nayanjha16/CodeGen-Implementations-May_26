package org.example.patterns;
public class SyncInterpreterTest {
    public static void main(String[] args) {
        SyncInterpreter i = new SyncInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
