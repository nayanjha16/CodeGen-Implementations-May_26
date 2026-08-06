package org.example.patterns;
public class BackupIteratorTest {
    public static void main(String[] args) {
        BackupCollection col = new BackupCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("backup:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
