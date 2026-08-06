package org.example.patterns;
public class BackupFlyweightTest {
    public static void main(String[] args) {
        BackupFlyweightFactory f = new BackupFlyweightFactory();
        String a = f.intern("a");
        String b = f.intern("a");
        if (a != b) throw new AssertionError();
        if (f.size() != 1) throw new AssertionError();
        System.out.println("ok");
    }
}
