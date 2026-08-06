package org.example.patterns;
public class StorageInterpreterTest {
    public static void main(String[] args) {
        StorageInterpreter i = new StorageInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
