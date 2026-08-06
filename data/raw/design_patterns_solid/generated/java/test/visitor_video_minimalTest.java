package org.example.patterns;
public class VideoVisitorTest {
    public static void main(String[] args) {
        String out = new VideoLeaf("n").accept(new VideoPrintVisitor());
        if (!out.equals("video:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
