package org.example.patterns;
public class ConfigIteratorTest {
    public static void main(String[] args) {
        ConfigCollection col = new ConfigCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("config:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
