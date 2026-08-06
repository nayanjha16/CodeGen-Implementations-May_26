package org.example.patterns;
public class StorageAdapterTest {
    public static void main(String[] args) {
        StorageTarget t = new StorageAdapter(new StorageLegacyApi());
        if (!t.fetch().equals("modern-storage")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}
