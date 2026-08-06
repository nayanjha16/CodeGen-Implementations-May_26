package org.example.patterns;
public class SyncSingletonTest {
    public static void main(String[] args) {
        SyncSingleton a = SyncSingleton.getInstance();
        SyncSingleton b = SyncSingleton.getInstance();
        a.setValue("sync-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("sync-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
