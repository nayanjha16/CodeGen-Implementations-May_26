package org.example.patterns;
public class BackupInterpreterTest {
    public static void main(String[] args) {
        BackupInterpreter i = new BackupInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
