package org.example.patterns;
public class VideoIteratorTest {
    public static void main(String[] args) {
        VideoCollection col = new VideoCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("video:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
