package org.example.patterns;
public class SyncAdapterTest {
    public static void main(String[] args) {
        SyncTarget t = new SyncAdapter(new SyncLegacyApi());
        if (!t.fetch().equals("modern-sync")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
