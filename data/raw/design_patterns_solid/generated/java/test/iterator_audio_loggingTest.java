package org.example.patterns;
public class AudioIteratorTest {
    public static void main(String[] args) {
        AudioCollection col = new AudioCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("audio:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
